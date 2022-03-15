

from Polls.models import Acao, Perfil
from Polls.simulation import calculaSimulacoes
from Portfolio.stockPrediction import PrevisaoAcoes
import numpy as np
from sklearn import cluster, covariance


class CategorizacaoAcoes():

    def primeiraCategorizacao():
        # Busca a primeira simulação, para pegar as datas
        simula = calculaSimulacoes.getPrimeiraSimulacao()

        # Pega todas as ações
        Acoes = Acao.objects.all()

        dfs = []
        codigos = []
        for acao in Acoes:

            # Busca as informações sobre as ações no periodo
            df = PrevisaoAcoes.getValoresBolsa(
                acao.codigo, simula.data_ini, simula.data_fim)
            if (not df.empty):
                codigos.append(acao.codigo)
                dfs.append(df)

        names = np.array(sorted(codigos)).T

        close_prices = np.vstack([q["Close"] for q in dfs])
        open_prices = np.vstack([q["Open"] for q in dfs])

        # The daily variations of the quotes are what carry most information
        variation = close_prices - open_prices

        clusters = CategorizacaoAcoes.clusterizacao(variation, names)

        for cl in clusters:
            len = cl.size
            for i in range(len):
                print(cl[i])

        CategorizacaoAcoes.iniciaPosClusterizacao(clusters)

    def iniciaPosClusterizacao(clusters):
        # Verifica quantos perfis existem para fazer o reagrupamento
        qtdePerfis = CategorizacaoAcoes.getQtdeNeceClusters()

        # se a quantidade de perfis for igual ao dos clusters, então não precisa fazer nada
        if (qtdePerfis == clusters.size):
            # TODO salvar qual cluster a ação faz parte
            return

        if (qtdePerfis > clusters.size):
            # se tiver mais perfis
            pass
        else:
            # se tiver mais clusters
            pass

    def salvaClusterAcao(acao, cluster):
        ac = Acao.objects.filter(codigo=acao)

        if (ac.count() == 0):
            print('Acao nao encontrada: ' + acao)
            return

        # TODO
        #ac.cluster = cluster
        ac.save()

    def getQtdeNeceClusters():
        return Perfil.objects.all().count()

    def clusterizacao(value, acoesNomes):
        # #############################################################################
        # Learn a graphical structure from the correlations
        edge_model = covariance.GraphicalLassoCV()

        # standardize the time series: using correlations rather than covariance
        # is more efficient for structure recovery
        X = value.copy().T
        X /= X.std(axis=0)
        edge_model.fit(X)

        # #############################################################################
        # Cluster using affinity propagation
        _, labels = cluster.affinity_propagation(
            edge_model.covariance_, random_state=0)
        n_labels = labels.max()

        clusters = []
        for i in range(n_labels + 1):
            clusters.append(acoesNomes[labels == i])

        return clusters
