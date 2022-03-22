

from re import I
from Polls.models import Acao, Perfil
from Polls.simulation import calculaSimulacoes
from Portfolio.stockPrediction import PrevisaoAcoes
import numpy as np
import pandas as pd
from pandas_datareader import data
from sklearn import cluster, covariance
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class CategorizacaoAcoes():

    logCl = []

    def testeInfo():

        #qtdeAtributos = 6
        qtdePerfis = CategorizacaoAcoes.getQtdeNeceClusters()

        # Busca a primeira simulação, para pegar as datas
        simula = calculaSimulacoes.getSimulacaoInicial()

        # Pega todas as ações
        Acoes = Acao.objects.all()

        acoesDic = CategorizacaoAcoes.converteAcoesToDict(Acoes)

        # Carrega as informações das ações
        df = data.DataReader(list(acoesDic.values()), data_source='yahoo',
                             start=simula.data_ini, end=simula.data_fim)

        # Verifica o tamanho inicial do DF
        #inicial = len(df.columns) / qtdeAtributos

        # caso haja ações com problema no cadastro e os valores vierem NULL, então serão descartados
        df = df.dropna(how='all', axis=1)

        # salva a quantidade total de colunas para saber quantas ações estavam com problema
        #final = len(df.columns) / qtdeAtributos

        lenAcoes = len(acoesDic)

        # stock_open is numpy array of transpose of df['Open']
        stock_open = np.array(df['Open']).T
        # stock_close is numpy array of transpose of df['Close']
        stock_close = np.array(df['Close']).T

        movements = stock_close - stock_open

        # ‘sum_of_movement’ of a company is defined as sum of differences of closing and opening prices of all days.
        sum_of_movement = np.sum(movements, 1)

        # The company and its ‘sum_of_movement’ is printed.
        # Have positive ‘sum_of_movement’. Hence it is advisable to go long(buy) on these stocks.
        # Have negative ‘sum_of_movement’. Hence it is advisable to short(sell) the stocks.
        for i in range(lenAcoes):
            print('company:{}, Change:{}'.format(
                df['High'].columns[i], sum_of_movement[i]))

        # Define a normalizer
        normalizer = Normalizer()
        # Create Kmeans model
        kmeans = KMeans(n_clusters=qtdePerfis, max_iter=1000)
        # Make a pipeline chaining normalizer and kmeans
        pipeline = make_pipeline(normalizer, kmeans)
        # Fit pipeline to daily stock movements
        pipeline.fit(movements)
        labels = pipeline.predict(movements)

        df1 = pd.DataFrame({'labels': labels, 'companies': list(
            acoesDic)}).sort_values(by=['labels'], axis=0)
        print(df1)

    def converteAcoesToDict(acoes):
        dicti = dict()
        for acao in acoes:

            try:
                data.DataReader(acao.codigo + '.SA', data_source='yahoo',
                                start='01-01-2020', end='05-01-2020')
                dicti[acao.nome] = acao.codigo + '.SA'
            except:
                continue

        return dicti

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

        print(close_prices)

        # Busca os dados da variaçao de preços (fechamento - abertura) para gerar a variação
        variation = close_prices - open_prices

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
