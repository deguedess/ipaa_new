

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

        # Busca a primeira simulação, para pegar as datas
        simula = calculaSimulacoes.getSimulacaoInicial()

        # Pega todas as ações
        Acoes = Acao.objects.all()

        # converte as ações em dicionários para geração da clusterização
        acoesDic = CategorizacaoAcoes.converteAcoesToDict(Acoes)

        # Carrega as informações das ações
        df = data.DataReader(list(acoesDic.values()), data_source='yahoo',
                             start=simula.data_ini, end=simula.data_fim)

        lenAcoes = len(acoesDic)  # Qtde de ações com dados

        # Busca as informações dos preços de abertura
        stock_open = np.array(df['Open']).T
        # Busca as informações dos preços de fechamento
        stock_close = np.array(df['Close']).T

        movements = stock_close - stock_open

        # a Soma de movimentação de uma companhia é definido somando as diferenças de fechamento e abertura durante os dias
        sum_of_movement = np.sum(movements, 1)

        # Tendo uma soma positiva, significa COMPRA
        # Tendo uma soma negativa, significa VENDA
        for i in range(lenAcoes):
            print('company:{}, Change:{}'.format(
                df['High'].columns[i], sum_of_movement[i]))

        dfClu = CategorizacaoAcoes.iniciaClusterizacao(movements, acoesDic)

        for i in range(len(dfClu.index)):

            CategorizacaoAcoes.salvaClusterAcao(
                acao=dfClu['companies'][i], cluster=dfClu['labels'][i])

    def iniciaClusterizacao(values, acoesDic):
        # Define a normalizer
        normalizer = Normalizer()
        # Reduce the data
        reduced_data = PCA(n_components=2)
        # Create Kmeans model
        kmeans = KMeans(
            n_clusters=CategorizacaoAcoes.getQtdeClusters(), max_iter=1000)
        # Make a pipeline chaining normalizer and kmeans
        pipeline = make_pipeline(normalizer, reduced_data, kmeans)
        # Fit pipeline to daily stock movements
        pipeline.fit(values)
        labels = pipeline.predict(values)

        return pd.DataFrame({'labels': labels, 'companies': list(
            acoesDic.values())}).sort_values(by=['labels'], axis=0)

    def converteAcoesToDict(acoes):
        dicti = dict()
        for acao in acoes:

            try:
                # é usado apenas para verificar se a ação é valida
                data.DataReader(acao.codigo + '.SA', data_source='yahoo',
                                start='01-01-2020', end='05-01-2020')
                dicti[acao.nome] = acao.codigo + '.SA'
            except:
                continue

        return dicti

    # Metodo que salva qual cluster a Ação faz parte

    def salvaClusterAcao(acao, cluster):
        acao = acao.replace('.SA', '')

        ac = Acao.objects.get(codigo=acao)

        if (ac == None):
            print('Acao nao encontrada: ' + acao)
            return

        ac.classificacao_ia = cluster
        ac.save()
        CategorizacaoAcoes.logCl.append(
            'Acao: ' + acao + ' - ' + str(cluster))

    def getQtdeClusters():
        return Perfil.objects.all().count()
