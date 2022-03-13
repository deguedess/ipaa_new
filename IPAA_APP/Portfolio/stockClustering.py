

from Polls.models import Acao
from Polls.simulation import calculaSimulacoes
from Portfolio.stockPrediction import PrevisaoAcoes
import numpy as np
from sklearn import cluster, covariance, manifold


class CategorizacaoAcoes():

    def categoriza():
        # Busca a primeira simulação, para pegar as datas
        simula = calculaSimulacoes.getPrimeiraSimulacao()

        # Pega todas as ações
        Acoes = Acao.objects.all()

        dfs = []
        for acao in Acoes:

            # Busca as informações sobre as ações no periodo
            df = PrevisaoAcoes.getValoresBolsa(
                acao.codigo, simula.data_ini, simula.data_fim)
            if (not df.empty):
                dfs.append(df)

        close_prices = np.vstack([q["Close"] for q in dfs])
        open_prices = np.vstack([q["Open"] for q in dfs])

        # The daily variations of the quotes are what carry most information
        variation = close_prices - open_prices

        # #############################################################################
        # Learn a graphical structure from the correlations
        edge_model = covariance.GraphicalLassoCV()

        # standardize the time series: using correlations rather than covariance
        # is more efficient for structure recovery
        X = variation.copy().T
        X /= X.std(axis=0)
        edge_model.fit(X)

        # #############################################################################
        # Cluster using affinity propagation

        _, labels = cluster.affinity_propagation(
            edge_model.covariance_, random_state=0)
        n_labels = labels.max()

        for i in range(n_labels + 1):
            print(labels[i])

            #print("Cluster %i: %s" % ((i + 1), ", ".join(Acoes[labels == i])))
