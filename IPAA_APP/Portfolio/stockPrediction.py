

from typing import final
from Polls.models import Acao
import pandas as pd
from pandas_datareader import data as web
from datetime import timedelta
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, LSTM
import math
from sklearn.preprocessing import MinMaxScaler
from Polls.simulation import calculaSimulacoes


from Simulation.models import Simulacao_acao


class PrevisaoAcoes():

    info = []

    def getAcoes(simAcao):
        acoes = []
        for sim in simAcao:
            acoes.append(sim.acao)

        return acoes

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

    def calculaPrevisaoSimulacao(simulacao, pos):
        AcoesSimula = PrevisaoAcoes.getAcoes(
            Simulacao_acao.objects.filter(simulacao=simulacao))

        Acoes = Acao.objects.all()

        # cria uma lista para armazenar as infos e erros

        PrevisaoAcoes.info.append('Calculando os valores para: ' +
                                  str(simulacao.nome))

        firstSim = calculaSimulacoes.getSimulacaoInicial()

        if (firstSim == simulacao):
            dias = 0  # se for a primeira, deve pegar os valores reais, ou seja, executa a leitura e salva os valores reais

        dias = abs((simulacao.data_fim - simulacao.data_ini).days)

        # dias usados no treinamento
        dTraining = dias * 2

        for acao in Acoes:

            if (acao in AcoesSimula):

                PrevisaoAcoes.info.append('Ação ' + str(acao.codigo) +
                                          ' já cadastrada ')

            else:
                final_data = PrevisaoAcoes.getValoresBolsa(
                    acao.codigo, firstSim.data_ini, firstSim.data_fim)

                if (final_data.empty):
                    PrevisaoAcoes.info.append('Ação ' + str(acao.codigo) +
                                              ' não encontrada na base do Yahoo')
                    continue

                if (firstSim == simulacao):
                    PrevisaoAcoes.salvaSimulacao(
                        simulacao, acao, final_data['Close'].iloc[0], final_data['Close'].iloc[-1], None)
                    continue

                # Busca as previsoes
                dfPred = PrevisaoAcoes.iniciaPrevisao(
                    final_data=final_data.filter(['Close']), dTraining=dTraining)

                PrevisaoAcoes.salvaSimulacao(
                    simulacao, acao, None, dfPred['Predictions'].iloc[-1], pos)

                PrevisaoAcoes.info.append('Valores da Ação ' + str(acao.codigo) +
                                          ' foram cadastrados com sucesso')

    def iniciaPrevisao(final_data, dTraining):

        # 1. Pega somente os valores de fechamento
        close_data = final_data

        # 2. Converte em Array
        dataset = close_data.values

        # 3. Faz a normalização dos valores para 0 ou 1
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)

        # 4. Criando um dataset de treinamento com 70% dos dados
        training_data_len = math.ceil(len(dataset) * .7)
        # pega somente os valores referentes ao 70%
        train_data = scaled_data[0:training_data_len, :]

        # 5. Separação entre x e y
        x_train_data = []  # sao valores reais
        y_train_data = []  # prediçao

        for i in range(dTraining, training_data_len):
            x_train_data = list(x_train_data)
            y_train_data = list(y_train_data)
            x_train_data.append(train_data[i-dTraining:i, 0])
            y_train_data.append(train_data[i, 0])

            # 6. Converting the training x and y values to numpy arrays
            x_train_data1, y_train_data1 = np.array(
                x_train_data), np.array(y_train_data)

            # 7. Reshaping training s and y data to make the calculations easier
            x_train_data2 = np.reshape(
                x_train_data1, (x_train_data1.shape[0], x_train_data1.shape[1], 1))

        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True,
                       input_shape=(x_train_data2.shape[1], 1)))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dense(units=25))
        model.add(Dense(units=1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(x_train_data2, y_train_data1,
                  batch_size=1, epochs=1)

        # 1. Creating a dataset for testing
        test_data = scaled_data[training_data_len - dTraining:, :]

        x_test = []
        #y_test = dataset[training_data_len:, :]
        for i in range(dTraining, len(test_data)):
            x_test.append(test_data[i-dTraining:i, 0])

        # 2.  Convert the values into arrays for easier computation
        x_test = np.array(x_test)
        x_test = np.reshape(
            x_test, (x_test.shape[0], x_test.shape[1], 1))

        # 3. Making predictions on the testing data
        predictions = model.predict(x_test)
        predictions = scaler.inverse_transform(predictions)

        # RMSE is the root mean squared error, which helps to measure the accuracy of the model.
        #rmse = np.sqrt(np.mean(((predictions - y_test)**2)))

        #train = df[:training_data_len]
        valid = final_data[training_data_len:]

        valid['Predictions'] = predictions

        return valid
