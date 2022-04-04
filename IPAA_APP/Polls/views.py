from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from Polls.models import Simulacao_cenarios
from Polls.portfolio import calculaPortfolio
from Polls.security import checkAccess
from Polls.simulation import calculaSimulacoes
from Portfolio.stockClustering import CategorizacaoAcoes
from Portfolio.stockPrediction import PrevisaoAcoes
from Portfolio.stockProfile import PerfilInvestimento
from .forms import RegisterUserForm, SurveyForm, PortfolioForm, SimulatiomForm


# PAGINA INICIAL
def index(request):
    form = RegisterUserForm()

    if request.method == 'POST':
        try:
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                request.session['usuario'] = user.id
                request.session['url'] = 'IPAA:polls'
                request.session['simula'] = None
                request.session['trava'] = False

                return redirect('IPAA:polls')
            else:
                for field in form:
                    print("Field Error:", field.name,  field.errors)
        except Exception as e:
            print(e)
            raise

    context = {
        'form': form,
    }

    return render(request, 'index.html', context)

# PAGINA DE AGRUPAMENTO DE AÇÕES


def configCluster(request):

    simulacoes = Simulacao_cenarios.objects.all()

    info = []
    for simula in simulacoes:

        # Categoriza conforme dados reais
        if (simula.id == calculaSimulacoes.getSimulacaoInicial().id):
            CategorizacaoAcoes.clusterizaoPrimeiroCenario(simula=simula)
        else:
            # Categoriza conforme previsao
            CategorizacaoAcoes.clusterizacaoCenariosSimulacao(simula=simula)
            print('')

        info.extend(CategorizacaoAcoes.logCl)

    context = {
        'infos': info,
    }

    return render(request, 'configCluster.html', context)

# PAGINA DE PREVISAO DOS VALORES DAS AÇÕES


def config(request):

    simulacoes = calculaSimulacoes.getAllSimulacao()
    pos = 0
    PrevisaoAcoes.info = []

    for simula in simulacoes:
        PrevisaoAcoes.calculaPrevisaoSimulacao(simula, pos)
        pos += 1

    context = {
        'infos': PrevisaoAcoes.info,
    }

    return render(request, 'config.html', context)

# PAGINA DE PERGUNTAS


def polls(request):

    userid = request.session['usuario']

    if (checkAccess.canAccessPolls(userid) == False):
        return redirect('IPAA:error')

    form = SurveyForm()

    if request.method == 'POST':
        try:
            form = SurveyForm(request.POST)
            if form.is_valid():
                form = form.save(userid)
                request.session['url'] = 'IPAA:portfolio'
                return redirect('IPAA:portfolio')
            else:
                for field in form:
                    print("Field Error:", field.name,  field.errors)
        except Exception as e:
            print(e)
            raise

    context = {
        "form": form,
    }
    return render(request, 'polls.html', context)

# PAGINA DA GERAÇÃO DA CARTEIRA


def portfolio(request):
    userid = request.session['usuario']

    tipo = userid % 2

    if (request.session['trava'] and checkAccess.canAccessSimulation(userid, None) == False):
        return redirect('IPAA:error')

    perf = calculaPortfolio.verificaPerfil(userid)

    acoesRec = None

    if (tipo == 0):  # busca as recomendações de IA
        acoesRec = PerfilInvestimento.getAcoesByPerfil(
            perf, calculaSimulacoes.getSimulacaoInicial())

    # cria a carteira inicial sem ações
    cart = calculaPortfolio.criaCarteiraSemAcoes(
        userid, tipo)

    form = PortfolioForm(acoesRec)

    if request.method == 'POST':
        form = PortfolioForm(acoesRec, request.POST)

        if form.is_valid():
            selected = form.save()

            idSimula = calculaSimulacoes.getPrimeiraSimulacao().id

            request.session['url'] = 'IPAA:simulation'
            request.session['simula'] = idSimula

            calculaPortfolio.salvaPortfolio(cart, selected, acoesRec, None)
            calculaPortfolio.criaAcoesCarteira(cart, selected)

            request.session['cenario_atual'] = 1
            return HttpResponseRedirect(reverse('IPAA:simulation', args=(idSimula,)))
        else:
            for field in form:
                print("Field Error:", field.name,  field.errors)

    context = {
        "perf": perf,
        "form": form,
        "cart": cart,
    }
    return render(request, 'portfolio.html', context)

# PAGINA DAS SIMULAÇÕES


def simulation(request, pk):

    userid = request.session['usuario']
    request.session['trava'] = True

    simulacao = get_object_or_404(Simulacao_cenarios, id=pk)

    if (checkAccess.canAccessSimulation(userid, simulacao) == False):
        return redirect('IPAA:error')

    form = SimulatiomForm()

    # Busca a carteira do usuario
    cartUser = SimulatiomForm.getCarteira(userid)

    qtde = calculaSimulacoes.getQtdeSimulacoes()

    ultimoCenario = not request.session['cenario_atual'] < qtde

    acoesRec = None

    print(cartUser.usuario)

    if (cartUser.tipo_grupo == 0):  # Busca as recomendações de IA
        acoesRec = PerfilInvestimento.getAcoesByPerfil(
            cartUser.usuario.perfil, simulacao)

    # Criar os campos na tela
    SimulatiomForm.getAcoesSimulacao(form, simulacao, ultimoCenario, acoesRec)

    listAll = calculaSimulacoes.getInfAcoesSimulacaoes(
        form, simulacao, cartUser)

    # busca o percentual
    percent = calculaSimulacoes.getPercentualCarteira(cartUser, simulacao)

    if request.method == 'POST':
        post = request.POST
        form = SimulatiomForm(post)

        form.cleanCheck(calculaSimulacoes.getAcoesSimulacoes(
            simulacao), post, ultimoCenario)

        if form.is_valid():

            # salva o percentual que a carteira subiu naquela simulação
            calculaSimulacoes.salvaCarteiraSimulacao(
                cartUser, percent, request.session['cenario_atual'])

            selected = form.save(
                calculaSimulacoes.getAcoesSimulacoes(simulacao), post)

            calculaPortfolio.salvaPortfolio(
                cartUser, selected, acoesRec, simulacao)

            if (not ultimoCenario):

                request.session['cenario_atual'] = request.session['cenario_atual'] + 1

                idSimula = calculaSimulacoes.getSimulacaoPos(
                    request.session['cenario_atual']).id

                request.session['url'] = 'IPAA:simulation'
                request.session['simula'] = idSimula

                return HttpResponseRedirect(reverse('IPAA:simulation', args=(idSimula,)))
            else:
                return redirect('IPAA:end')

        else:
            print('not valid')
            print(form.errors)
            for field in form:
                print("Field Error:", field.name,  field.errors)

    context = {
        "form": form,
        "simulacao": simulacao,
        "qtde": qtde,
        "atual": request.session['cenario_atual'],
        "lista": listAll,
        "percent": percent
    }
    return render(request, 'simulation.html', context)

# PAGINA QUE O USUARIO INFORMA O MOTIVO


def motivo(request):

    if request.method == 'POST':

        print('POST')

    context = {
        # "percent": percent

    }

    return render(request, 'motivo.html', context)

# PAGINA FINAL


def end(request):

    if request.method == 'POST':

        print('POST')

    context = {
        # "percent": percent

    }

    return render(request, 'end.html', context)

# PAGINA DE ERRO


def error(request):
    #form = RegisterUserForm()

    url = request.session['url']

    if request.method == 'POST':

        idSimula = request.session['simula']

        if (idSimula == None):
            return HttpResponseRedirect(reverse(url))
        else:
            return HttpResponseRedirect(reverse(url, args=(idSimula,)))

    context = {
        # 'url': url,

    }

    return render(request, 'error.html', context)
