

from django import forms
from Polls.models import Simulacao_cenarios
from Portfolio.stockInfo import infoMercadoAcoes
from Simulation.models import Carteira_Simulacao, Simulacao_acao
from django.db.models import Sum


class calculaSimulacoes():

    def getQtdeSimulacoes():
        return Simulacao_cenarios.objects.all().count()-1

    def getSimulacaoPos(pos):
        return Simulacao_cenarios.objects.all().order_by('data_ini')[pos]

    def getSimulacaoPre(atual):
        return Simulacao_cenarios.objects.all().order_by('data_ini')[atual-1]

    def getPrimeiraSimulacao():
        return Simulacao_cenarios.objects.all().order_by('data_ini')[1]

    def getAllSimulacao():
        return Simulacao_cenarios.objects.all().order_by('data_ini')

    def getSimulacaoInicial():
        return Simulacao_cenarios.objects.all().order_by('data_ini')[0]

    def getUltimaSimulacao():
        return Simulacao_cenarios.objects.all().order_by('data_ini')[calculaSimulacoes.getQtdeSimulacoes()]

    def getAcoesSimulacoes(simulacao):
        return Simulacao_acao.objects.filter(simulacao=simulacao)

    def getPrecoUltimaSimulacao(simulacaoPos, acao):
        simulacao = calculaSimulacoes.getSimulacaoPre(simulacaoPos)

        simulaA = Simulacao_acao.objects.filter(simulacao=simulacao, acao=acao)

        if simulaA == None:
            return 0.
        else:
            if simulaA.exists():
                return simulaA[0].valor_novo
            else:
                return 0.

    def getPercentualCarteira(carteira, simulacao):

        listaAcao = carteira.acoes.all()

        percent = 0
        for acao in listaAcao:
            simulas = Simulacao_acao.objects.filter(
                acao=acao, simulacao=simulacao)

            if (simulas):
                simulaAcao = simulas[0]
                percent += ((simulaAcao.valor_novo -
                             simulaAcao.valor_ant)/simulaAcao.valor_ant)*100

        return float(percent)

    def getPercentualAcumuladoCarteira(carteira):

        total = Carteira_Simulacao.objects.filter(carteira=carteira).aggregate(
            Sum('percentual'))['percentual__sum'] or 0.00

        return float(total)

    def salvaCarteiraSimulacao(carteira, percent, cenAtual):

        simula = calculaSimulacoes.getSimulacaoPre(cenAtual)

        cartSim = Carteira_Simulacao()
        cartSim.carteira = carteira
        cartSim.simulacao = simula
        cartSim.percentual = percent

        cartSim.save()

    def getInfAcoesSimulacaoes(form, simula, cart):

        simu = calculaSimulacoes.getAcoesSimulacoes(simula)

        listAll = []
        index = 0
        for field in form:
            ff = fieldInfo()
            ff.valorAntigo = simu[index].valor_ant
            ff.valorAtual = simu[index].valor_novo
            ff.percent = ((ff.valorAtual - ff.valorAntigo)/ff.valorAntigo)*100
            ff.field = field
            ff.carteira = True if simu[index].acao in cart.acoes.all(
            ) else False
            listAll.append(ff)
            index += 1

        return listAll

    def getInfAcoesPortofolio(form, simula):

        simu = calculaSimulacoes.getAcoesSimulacoes(simula)

        listAll = []
        index = 0
        for field in form:
            ff = fieldInfo()
            ff.valorAntigo = simu[index].valor_ant
            ff.valorAtual = simu[index].valor_novo
            ff.percent = getRentabilidade(ff, simula, simu[index].acao)
            ff.field = field
            ff.carteira = False
            listAll.append(ff)
            index += 1

        return listAll


def getRentabilidade(ff, simula, acao):

    antigo = ff.valorAntigo
    atual = ff.valorAtual

    splits = infoMercadoAcoes.getSplits(acao, simula.data_ini, simula.data_fim)

    # se houver splits, entao adiciona no calculo
    if (splits is not None):
        antigo = antigo * splits['value'].sum()

    return (atual / antigo) * 100


class fieldInfo():

    field = forms.BooleanField
    valorAntigo = 0.
    valorAtual = 0.
    percent = 0.
    carteira = False
