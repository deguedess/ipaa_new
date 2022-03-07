

from Polls.models import Acao
import pandas as pd
from pandas_datareader import data as web
from datetime import timedelta
import numpy as np

import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, LSTM
import math
from sklearn.preprocessing import MinMaxScaler


from Simulation.models import Simulacao_acao


class PrevisaoAcoes():

    def calculaPrevisaoSimulacao(simulacao):
        AcoesSimula = Simulacao_acao.objects.filter(simulacao=simulacao)
        Acoes = Acao.objects.all()

        dias = abs((simulacao.data_fim - simulacao.data_ini).days)

        # busca os dados de 1 ano até a data inicial #TODO usar + os dados historicos?
        data_ini_simula = simulacao.data_ini - timedelta(365)

        print(data_ini_simula)
        print(simulacao.data_ini)
        print(simulacao.data_fim)
        print(dias)

        # dias usados no treinamento
        dTraining = 100

        for acao in Acoes:
            if (acao not in AcoesSimula):
                df = pd.DataFrame()
                # try:
                df = web.DataReader(acao.codigo + ".SA", data_source='yahoo',
                                    start=data_ini_simula, end=simulacao.data_ini)

                df.reset_index(inplace=True)

                final_data = df

                # 1. Pega somente os valores de fechamento
                close_data = final_data.filter(['Close'])

                # 2. Converte em Array
                dataset = close_data.values

                # 3. Faz a normalização dos valores para 0 ou 1
                scaler = MinMaxScaler(feature_range=(0, 1))
                scaled_data = scaler.fit_transform(dataset)

                # 4. Criando um dataset de treinamento com 70% dos dados
                training_data_len = math.ceil(len(dataset) * .7)
                train_data = scaled_data[0:training_data_len, :]

                # 5. Separação entre x e y
                x_train_data = []
                y_train_data = []
                for i in range(dTraining, len(train_data)):
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
                y_test = dataset[training_data_len:, :]
                for i in range(dTraining, len(test_data)):
                    x_test.append(test_data[i-dTraining:i, 0])

                # 2.  Convert the values into arrays for easier computation
                x_test = np.array(x_test)
                x_test = np.reshape(
                    x_test, (x_test.shape[0], x_test.shape[1], 1))

                # 3. Making predictions on the testing data
                predictions = model.predict(x_test)
                predictions = scaler.inverse_transform(predictions)

                rmse = np.sqrt(np.mean(((predictions - y_test)**2)))

                train = df[:training_data_len]
                valid = df[training_data_len:]

                valid['Predictions'] = predictions

                #print(valid[['Close', 'Predictions']])

                return
               # except Exception as e:
                #    print(e)
