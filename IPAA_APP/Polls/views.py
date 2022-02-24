from django.http.response import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.urls import reverse

from Polls.models import Pergunta, Simulacao_cenarios, Usuario, Acao
from django.template import RequestContext, loader
from django.views import generic

from Polls.portfolio import calculaPortfolio
from Polls.security import checkAccess
from Polls.simulation import calculaSimulacoes, fieldInfo
from .forms import RegisterUserForm, SurveyForm, PortfolioForm, SimulatiomForm


# Create your views here.


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


def portfolio(request):
    userid = request.session['usuario']

    tipo = userid % 2

    if (request.session['trava'] and checkAccess.canAccessSimulation(userid, None) == False):
        return redirect('IPAA:error')

    perf = calculaPortfolio.verificaPerfil(userid)

    # TODO
    acoesRec = None

    if (tipo == 0):
        acoesRec = Acao.objects.order_by('codigo')[:3]

    cart = calculaPortfolio.criaCarteira(
        userid, tipo, acoesRec)

    form = PortfolioForm(cart.acoes.all())

    if request.method == 'POST':
        form = PortfolioForm(acoesRec, request.POST)

        if form.is_valid():
            selected = form.save()

            idSimula = calculaSimulacoes.getPrimeiraSimulacao().id

            request.session['url'] = 'IPAA:simulation'
            request.session['simula'] = idSimula

            calculaPortfolio.salvaPortfolio(cart, selected, acoesRec, None)
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


def simulation(request, pk):

    userid = request.session['usuario']
    request.session['trava'] = True

    simulacao = get_object_or_404(Simulacao_cenarios, id=pk)

    if (checkAccess.canAccessSimulation(userid, simulacao) == False):
        return redirect('IPAA:error')

    form = SimulatiomForm()

    # Busca a carteira do usuario
    cartUser = SimulatiomForm.getCarteira(userid)

    # Criar os campos na tela
    SimulatiomForm.getAcoesSimulacao(form, simulacao, cartUser)

    qtde = calculaSimulacoes.getQtdeSimulacoes()

    listAll = calculaSimulacoes.getInfAcoesSimulacaoes(form, simulacao)

    # busca o percentual
    percent = calculaSimulacoes.getPercentualCarteira(cartUser, simulacao)

    # TODO
    acoesRec = None

    if (cartUser.tipo_grupo == 0):
        acoesRec = Acao.objects.order_by('codigo')[:3]

    if request.method == 'POST':
        post = request.POST
        form = SimulatiomForm(post)

        if form.is_valid():

            # salva o percentual que a carteira subiu naquela simulação
            calculaSimulacoes.salvaCarteiraSimulacao(
                cartUser, percent, request.session['cenario_atual'])

            selected = form.save(
                calculaSimulacoes.getAcoesSimulacoes(simulacao), post)

            calculaPortfolio.salvaPortfolio(
                cartUser, selected, acoesRec, simulacao)

            if (request.session['cenario_atual'] < qtde):

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


def end(request):

    if request.method == 'POST':

        print('POST')

    context = {
        # "percent": percent

    }

    return render(request, 'end.html', context)


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


class UsuarioListView(generic.ListView):
    model = Usuario


class PerguntaListView(generic.ListView):
    model = Pergunta
    context_object_name = 'Perguntas'
    queryset = Pergunta.objects.filter()[:1]
    template_name = 'books/my_arbitrary_template_name_list.html'


class UserCreate(CreateView):
    model = Usuario
    fields = ['idade', 'genero', 'grau_instrucao', 'profissao']


def detail(request, question_id):
    question = get_object_or_404(Pergunta, pk=question_id)
    return render(request, 'detail.html', {'Pergunta': question})
