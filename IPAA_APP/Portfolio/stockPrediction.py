

from Polls.models import Acao
import pandas as pd
from pandas_datareader import data as web
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, LSTM
import math
from sklearn.preprocessing import MinMaxScaler
from Polls.simulation import calculaSimulacoes
from Simulation.models import Simulacao_acao


class PrevisaoAcoes():

    info = []

    # Retorna somente as ações que estao na lista de Ação_Simulação
    def getAcoes(simAcao):
        acoes = []
        for sim in simAcao:
            acoes.append(sim.acao)

        return acoes

    # Retorna os valores das ações na Bolsa
    def getValoresBolsa(acao, data_ini, data_fim):

        try:
            # busca os valores das ações no periodo definido na simulação
            df = web.DataReader(acao + ".SA", data_source='yahoo',
                                start=data_ini, end=data_fim)

            # remove a data como index
            df.reset_index(inplace=True)

            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()

    # Salva as informações da ação naquela simulação
    def salvaSimulacao(simulacao, acao, valorAnt, valorNovo, pos):
        simAcao = Simulacao_acao()
        simAcao.acao = acao
        simAcao.simulacao = simulacao

        simAcao.valor_novo = float(valorNovo)

        if valorAnt == None:
            simAcao.valor_ant = calculaSimulacoes.getPrecoUltimaSimulacao(
                pos, acao)
        else:
            simAcao.valor_ant = float(valorAnt)

        simAcao.classificacao_ia = ''

        simAcao.save()

    # Função que faz o calculo dos valores previstos
    def calculaPrevisaoSimulacao(simulacao, pos):
        # Busca as ações na simulação
        AcoesSimula = PrevisaoAcoes.getAcoes(
            Simulacao_acao.objects.filter(simulacao=simulacao))

        Acoes = Acao.objects.all()

        # cria uma lista para armazenar as infos e erros
        PrevisaoAcoes.info.append(
            '{} - Calculando os valores'.format(str(simulacao.nome)))

        firstSim = calculaSimulacoes.getSimulacaoInicial()

        if (firstSim == simulacao):
            dTraining = 0  # se for a primeira, deve pegar os valores reais, ou seja, executa a leitura e salva os valores reais
        else:
            #dias = abs((simulacao.data_fim - simulacao.data_ini).days)
            dTraining = simulacao.indice_previsao  # dias usados no treinamento

        for acao in Acoes:

            if (acao in AcoesSimula):
                # Caso ja esteja cadastrada, então nao faz nada
                PrevisaoAcoes.info.append(
                    '->  {} - Já cadastrada'.format(str(acao.codigo)))

            else:
                # Busca os valores reais da simulação inicial para fazer a previsão dos proximos meses
                final_data = PrevisaoAcoes.getValoresBolsa(
                    acao.codigo, firstSim.data_ini, firstSim.data_fim)

                if (final_data.empty):
                    PrevisaoAcoes.info.append(
                        '->  {} - Não foi encontrada na base do Yahoo'.format(str(acao.codigo)))
                    continue

                # Caso for a primeira simulação, apenas salva o primeiro e ultimo valor
                if (firstSim == simulacao):
                    PrevisaoAcoes.salvaSimulacao(
                        simulacao, acao, final_data['Close'].iloc[0], final_data['Close'].iloc[-1], None)
                    continue

                # Busca as previsoes
                dfPred = PrevisaoAcoes.iniciaPrevisao(
                    final_data=final_data.filter(['Close']), dTraining=dTraining)

                valorFinal = PrevisaoAcoes.addNoise(
                    simula=simulacao, valorIni=dfPred['Predictions'].iloc[0], valorFim=dfPred['Predictions'].iloc[-1], df=final_data)

                # Salva os valores da ações na simulação
                PrevisaoAcoes.salvaSimulacao(
                    simulacao, acao, None, valorFinal, pos)

                PrevisaoAcoes.info.append(
                    '->  {} - Valores foram cadastrados com sucesso'.format(str(acao.codigo)))

    # Função que faz o calculo da previsão
    def iniciaPrevisao(final_data, dTraining):

        # 1. Pega os valores e Converte em Array
        dataset = final_data.values

        # 2. Faz a normalização dos valores para 0 ou 1
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)

        # 3. Criando um dataset de treinamento com 70% dos dados
        training_data_len = math.ceil(len(dataset) * .7)

        # 4. Pega somente os valores referentes ao 70%
        train_data = scaled_data[0:training_data_len, :]

        # 5. Separação entre x e y
        x_train_data = []  # sao valores reais
        y_train_data = []  # prediçao

        # 6. Laço que entre a quantidade de dias passadas e o tamanho total do treinamento
        for i in range(dTraining, training_data_len):
            x_train_data = list(x_train_data)
            y_train_data = list(y_train_data)
            x_train_data.append(train_data[i-dTraining:i, 0])
            y_train_data.append(train_data[i, 0])

            # 7. Converte os valores em Arrays Numpy
            x_train_data1, y_train_data1 = np.array(
                x_train_data), np.array(y_train_data)

            # 8. Faz o reshape para facilitar o processo de calculo
            x_train_data2 = np.reshape(
                x_train_data1, (x_train_data1.shape[0], x_train_data1.shape[1], 1))

        # 9. Cria o modelo e adiciona os dados e as camadas
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True,
                       input_shape=(x_train_data2.shape[1], 1)))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dense(units=25))
        model.add(Dense(units=1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train_data2, y_train_data1,
                  batch_size=1, epochs=1)

        # 10. Cria o dataset que será usado para receber os valores da predição
        test_data = scaled_data[training_data_len - dTraining:, :]

        x_test = []
        for i in range(dTraining, len(test_data)):
            x_test.append(test_data[i-dTraining:i, 0])

        # 11. Converte os valores em Arrays e faz o Reshape
        x_test = np.array(x_test)
        x_test = np.reshape(
            x_test, (x_test.shape[0], x_test.shape[1], 1))

        # 12. Utiliza o modelo criado para fazer a predição dos valores
        predictions = model.predict(x_test)
        predictions = scaler.inverse_transform(predictions)

        valid = final_data[training_data_len:]

        # 13. Cria uma nova coluna no dataset chamada Predictions e adiciona os valores calculados
        valid['Predictions'] = predictions

        return valid

    def addNoise(simula, valorIni, valorFim, df):
        dif = valorFim - valorIni

        ret = np.log(df['Adj Close'] / df['Adj Close'].shift(1))

        value = (ret.std() * (simula.indice_previsao/2))

        # multiplica o desvio padrao em percentual com o valor final da ação
        value = (valorFim * (value * 10))/100

        if (dif < 0):
            value = value * -1

        return valorFim + value

    def getSplits(acao, data_ini, data_fim):
        df = PrevisaoAcoes.getActionsStock(
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
