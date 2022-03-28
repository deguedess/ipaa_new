
from Polls.models import Perfil
from Simulation.models import Simulacao_acao


class PerfilInvestimento():

    def getRelacaoBySimulacao(simula):
        # Busca as ações por ordem de desvio padrão
        acoesS = Simulacao_acao.objects.filter(
            simulacao=simula).order_by('desvio_padrao')

        # busca os perfis por ordem de peso_inicial
        perfis = Perfil.objects.all().order_by('peso_inicial')
        relacao = dict()

        acaoClu = []  # cria uma dicionário com as classificações de IA
        for ac in acoesS:
            if (ac.classificacao_ia not in acaoClu):
                acaoClu.append(ac.classificacao_ia)

        # Se houver menos classificações que perfis, houve um erro na geração
        if len(acaoClu) is not perfis.count():
            return None

        itera = 0
        for perfil in perfis:
            relacao[perfil.id] = acaoClu[itera]

            itera += 1

        return relacao

    def getAcoesByPerfil(perfil, simula):
        relacao = PerfilInvestimento.getRelacaoBySimulacao(simula)

        if relacao == None:
            return None

        acoesS = Simulacao_acao.objects.filter(
            simulacao=simula, classificacao_ia=relacao[perfil.id])

        acao = []
        for aca in acoesS:
            acao.append(aca.acao)

        return acao
