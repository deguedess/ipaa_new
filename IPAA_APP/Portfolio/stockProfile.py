
from Polls.models import Perfil
from Simulation.models import Simulacao_acao


class PerfilInvestimento():

    # TODO VALIDAR NULOS E VAZIOS
    def getRelacaoBySimulacao(simula):
        acoesS = Simulacao_acao.objects.filter(
            simulacao=simula).order_by('desvio_padrao')
        perfis = Perfil.objects.all().order_by('peso_inicial')
        relacao = dict()

        acaoClu = []
        for ac in acoesS:
            if (ac.classificacao_ia not in acaoClu):
                acaoClu.append(ac.classificacao_ia)

        itera = 0
        for perfil in perfis:
            relacao[perfil.id] = acaoClu[itera]

            itera += 1

        return relacao

    def getAcoesByPerfil(perfil, simula):
        relacao = PerfilInvestimento.getRelacaoBySimulacao(simula)

        acoesS = Simulacao_acao.objects.filter(
            simulacao=simula, classificacao_ia=relacao[perfil.id])

        acao = []
        for aca in acoesS:
            acao.append(aca.acao)

        return acao
