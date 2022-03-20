

from re import I
from Polls.models import Acao, Perfil
from Polls.simulation import calculaSimulacoes
from Portfolio.stockPrediction import PrevisaoAcoes
import numpy as np
import pandas as pd
from sklearn import cluster, covariance


class CategorizacaoAcoes():

    logCl = []

    def testeInfo():
        # Busca a primeira simulação, para pegar as datas
        simula = calculaSimulacoes.getSimulacaoInicial()

        # Pega todas as ações
        Acoes = Acao.objects.all()

        codigos = []
        dfs = []
        for acao in Acoes:
            cod = acao.codigo

            # Busca as informações sobre as ações no periodo
            df = PrevisaoAcoes.getValoresBolsa(
                cod, simula.data_ini, simula.data_fim)
            if (not df.empty):

                codigos.append(cod)
                sec_data = df['Adj Close']
                # retorno diario
                sec_returns = np.log(sec_data / sec_data.shift(1))

                df['Media'] = sec_returns.mean() * 250
                df['Desvio'] = sec_returns.std() * 250 ** 0.5

                print('====> ' + cod)

                dfs.append(df)

        names = np.array(sorted(codigos)).T

        std_prices = np.vstack([q["Desvio"] for q in dfs])
        mean_prices = np.vstack([q["Media"] for q in dfs])

        std_prices = std_prices[~np.isnan(std_prices)]

        print(std_prices)

        # Gera os primeiros clusters
        clusters = CategorizacaoAcoes.clusterizacao(
            std_prices, names)
        print(clusters)

    def primeiraCategorizacao():
        CategorizacaoAcoes.logCl = []

        # Busca a primeira simulação, para pegar as datas
        simula = calculaSimulacoes.getSimulacaoInicial()

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

        # Busca os dados da variaçao de preços (fechamento - abertura) para gerar a variação
        variation = close_prices - open_prices

        print(variation)

        # Gera os primeiros clusters
        clusters = CategorizacaoAcoes.clusterizacao(variation, names)

        # Inicia o processo de configuração e salvamento das informações no banco
        CategorizacaoAcoes.iniciaPosClusterizacao(clusters)

    def iniciaPosClusterizacao(clusters):
        # Verifica quantos perfis existem para fazer o reagrupamento
        qtdePerfis = CategorizacaoAcoes.getQtdeNeceClusters()

        # se a quantidade de perfis for igual ao dos clusters, então não precisa fazer nada
        if (qtdePerfis == len(clusters)):

            for cl in clusters:
                tam = cl.size
                for i in range(tam):
                    CategorizacaoAcoes.salvaClusterAcao(
                        cl[i], 'Cluster ' + str(i))
            return

        if (qtdePerfis > len(clusters)):
            # se tiver mais perfis
            dif = qtdePerfis - len(clusters)

            for cl in clusters:
                tam = cl.size
                for i in range(tam):
                    CategorizacaoAcoes.salvaClusterAcao(
                        cl[i], 'Cluster ' + str(i))

        else:
            # se tiver mais clusters
            dif = len(clusters) - qtdePerfis

            for cl in clusters:
                tam = cl.size
                for i in range(tam):
                    CategorizacaoAcoes.salvaClusterAcao(
                        cl[i], 'Cluster ' + str(i))

    # Metodo que salva qual cluster a Ação faz parte
    def salvaClusterAcao(acao, cluster):
        ac = Acao.objects.get(codigo=acao)

        if (ac == None):
            print('Acao nao encontrada: ' + acao)
            return

        ac.classificacao_ia = cluster
        ac.save()
        CategorizacaoAcoes.logCl.append(
            'Acao: ' + acao + ' - ' + cluster)

    def getQtdeNeceClusters():
        return Perfil.objects.all().count()

    # Metodo que faz o processo de Clusterização
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
            print(acoesNomes[labels == i])
            clusters.append(acoesNomes[labels == i])

        return clusters
