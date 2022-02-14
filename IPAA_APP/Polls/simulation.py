

from django import forms
from Polls.models import Simulacao_cenarios
from Simulation.models import Simulacao_acao


class calculaSimulacoes():

    def getQtdeSimulacoes():
        return Simulacao_cenarios.objects.all().count()-1

    def getSimulacaoPos(pos):
        return Simulacao_cenarios.objects.all().order_by('data_ini')[pos]

    def getPrimeiraSimulacao():
        return Simulacao_cenarios.objects.all().order_by('data_ini')[1]

    def getAcoesSimulacoes(simulacao):
        return Simulacao_acao.objects.filter(simulacao=simulacao)

    def getInfAcoesSimulacaoes(form, simula):

        simu = calculaSimulacoes.getAcoesSimulacoes(simula)

        listAll = []
        index = 0
        for field in form:
            ff = fieldInfo()
            ff.valorAntigo = simu[index].valor_ant
            ff.valorAtual = simu[index].valor_novo
            ff.percent = ((ff.valorAtual - ff.valorAntigo)/ff.valorAntigo)*100
            ff.field = field
            listAll.append(ff)
            index += 1

        return listAll


class fieldInfo():

    field = forms.BooleanField
    valorAntigo = 0.
    valorAtual = 0.
    percent = 0.
