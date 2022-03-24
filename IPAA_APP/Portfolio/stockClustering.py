

import datetime
from re import I
from Polls.models import Acao, Perfil
import numpy as np
import pandas as pd
from pandas_datareader import data
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from Simulation.models import Simulacao_acao


class CategorizacaoAcoes():

    logCl = []

    def iniciaDicionario():
        # Pega todas as ações
        Acoes = Acao.objects.all()

        # converte as ações em dicionários para geração da clusterização
        return CategorizacaoAcoes.converteAcoesToDict(Acoes)

    # Usa dados reais do passado para fazer a primeira clusterização
    def clusterizaoPrimeiroCenario(simula):
        acoesDic = CategorizacaoAcoes.iniciaDicionario()

        # Carrega as informações das ações
        df = data.DataReader(list(acoesDic.values()), data_source='yahoo',
                             start=simula.data_ini, end=simula.data_fim)

        # lenAcoes = len(acoesDic)  # Qtde de ações com dados

        # Busca as informações dos preços de abertura
        stock_open = np.array(df['Open']).T
        # Busca as informações dos preços de fechamento
        stock_close = np.array(df['Close']).T

        movements = stock_close - stock_open

        # a Soma de movimentação de uma companhia é definido somando as diferenças de fechamento e abertura durante os dias
        sum_of_movement = np.sum(movements, 1)

        # Tendo uma soma positiva, significa COMPRA
        # Tendo uma soma negativa, significa VENDA
        # for i in range(lenAcoes):
        # print('company:{}, Change:{}'.format(
        # df['High'].columns[i], sum_of_movement[i]))

        CategorizacaoAcoes.iniciaProcesso(df=df, movements=movements, acoesDic=acoesDic,
                                          simula=simula, sumOfMovement=sum_of_movement)

    # Usa os próprios dados gerados pelo sistema (previsões) para fazer a clusterização
    def clusterizacaoCenariosSimulacao(simula):

        acoesDic = CategorizacaoAcoes.iniciaDicionario()

        precoAnt = []
        precoFin = []

        for acao in list(acoesDic.values()):
            acao = acao.replace('.SA', '')

            ac = Acao.objects.get(codigo=acao)
            acaoS = Simulacao_acao.objects.get(simulacao=simula, acao=ac)

            precoAnt.append(acaoS.valor_ant)
            precoFin.append(acaoS.valor_novo)

        df = pd.DataFrame({'Acao': acoesDic.values(), 'Open': precoAnt,
                           'Close': precoFin, 'Adj Close': None})

        df.set_index("Acao", inplace=True)

        # Busca as informações dos preços de abertura
        stock_open = np.array(df['Open']).T
        # Busca as informações dos preços de fechamento
        stock_close = np.array(df['Close']).T

        movements = stock_close - stock_open

        df['Adj Close'] = movements

        # a Soma de movimentação de uma companhia é definido somando as diferenças de fechamento e abertura durante os dias
        sum_of_movement = np.sum(movements, 0)

        CategorizacaoAcoes.iniciaProcesso(df=df, movements=movements, acoesDic=acoesDic,
                                          simula=simula, sumOfMovement=sum_of_movement)

    def iniciaProcesso(df, movements, acoesDic, simula, sumOfMovement):

        # Clusterização das ações
        dfClu = CategorizacaoAcoes.iniciaClusterizacao(movements, acoesDic)
        # Busca os outros valores
        otrVal = CategorizacaoAcoes.calculaValorRetornoeDesvio(
            df=df, diction=acoesDic, simula=simula)

        for i in range(len(dfClu.index)):

            CategorizacaoAcoes.salvaClusterAcao(
                acao=dfClu['companies'][i], cluster=dfClu['labels'][i], simula=simula, moviment=sumOfMovement[i],
                desvioP=otrVal['Desvio'][i], retornoF=otrVal['Retorno'][i])

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

    # Metodo que calcula o valor de retorno de uma ação a aprtir da data inicial até a final
    def calculaValorRetornoeDesvio(df, diction, simula):
        retornoFinal = []
        desvioPadrao = []

        diasUteis = CategorizacaoAcoes.getDiasUteis(
            simula.data_ini, simula.data_fim)

        for com in list(diction.values()):
            retDiario = df['Close'][com].pct_change()
            retDiario = (retDiario + 1).cumprod()-1
            retornoFinal.append(retDiario[len(retDiario)-1])

            ret = np.log(df['Adj Close'][com] / df['Adj Close'][com].shift(1))
            desv = ret.std() * diasUteis ** 0.5
            desvioPadrao.append(desv)

        return pd.DataFrame({'Retorno': retornoFinal, 'Desvio': desvioPadrao})

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

    def salvaClusterAcao(acao, cluster, simula, moviment, retornoF, desvioP):
        acao = acao.replace('.SA', '')

        ac = Acao.objects.get(codigo=acao)

        if (ac == None):
            CategorizacaoAcoes.logCl.append(
                'Ação  não encontrada: ' + acao)
            return

        simAc = Simulacao_acao.objects.get(acao=ac, simulacao=simula)

        if (simAc == None):
            CategorizacaoAcoes.logCl.append(
                'Simulação: {} não encontrada para ação: {}'.format(simula, acao))
            return

        simAc.valor_movimentacao = moviment
        simAc.classificacao_ia = cluster
        simAc.valor_retorno = retornoF
        simAc.desvio_padrao = desvioP
        simAc.save()
        CategorizacaoAcoes.logCl.append(
            'Ação {} para Simulação {} - Cluster: {}'.format(acao, simula, cluster))

    def getQtdeClusters():
        return Perfil.objects.all().count()

    def getDiasUteis(a, b):
        return sum(1 for day in CategorizacaoAcoes.iterdates(a, b) if day.weekday not in (5, 6))

    def iterdates(date1, date2):
        one_day = datetime.timedelta(days=1)
        current = date1
        while current < date2:
            yield current
            current += one_day
