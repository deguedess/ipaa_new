
import pandas as pd
from pandas_datareader import data as web
import numpy as np

from Simulation.models import Simulacao_acao


class infoMercadoAcoes():

    # Retorna as informações das ações na Bolsa (actions = SPLIT e DIVIDEND)
    def getActionsStock(acao, data_ini, data_fim):

        try:
            # busca os valores das ações no periodo definido na simulação
            df = web.DataReader(acao + ".SA", data_source='yahoo-actions',
                                start=data_ini, end=data_fim)

            # remove a data como index
            # df.reset_index(inplace=True)

            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()

    def getSplits(acao, data_ini, data_fim):
        df = infoMercadoAcoes.getActionsStock(
            acao=acao, data_fim=data_fim, data_ini=data_ini)

        if df.empty:
            return None

        dfsplit = df[(df.action == 'SPLIT')]

        if dfsplit.empty:
            return None

        # SAlva na ação que houve SPLIT
        acao.split = True
        acao.save()

        return dfsplit

    def saveDividend(acao, simulacao):
        df = infoMercadoAcoes.getActionsStock(
            acao=acao.codigo, data_fim=simulacao.data_fim, data_ini=simulacao.data_ini)

        if df.empty:
            return

        somaDiv = df[(df.action == 'DIVIDEND')]['value'].sum()

        acaoSimula = Simulacao_acao.objects.get(acao=acao, simulacao=simulacao)

        acaoSimula.dividend_yeld = somaDiv / float(acaoSimula.valor_novo)
        acaoSimula.save()

    def diff_month(d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
