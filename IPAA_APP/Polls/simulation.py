

from Polls.models import Simulacao_cenarios


class calculaSimulacoes():


    
    def getQtdeSimulacoes():
        return Simulacao_cenarios.objects.all().count()-1

    def getSimulacaoPos(pos):
        return Simulacao_cenarios.objects.all().order_by('data_ini')[pos]

    def getPrimeiraSimulacao():
        return Simulacao_cenarios.objects.all().order_by('data_ini')[1]



    