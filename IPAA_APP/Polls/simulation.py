

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




    