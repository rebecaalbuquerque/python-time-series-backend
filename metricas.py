import sklearn.metrics as metrics
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from constants import PATH_METRICAS


# obsercacoes e predicoes são pd.Series
from utils import arquivo_para_base64, limpar_diretorio


def gerar_metricas_e_plot_predicoes(nome_serie_temporal, df_observacoes, df_predicoes):
    limpar_diretorio(PATH_METRICAS)

    # Setando index dos DataFrames como um DateTime
    df_observacoes[df_observacoes.columns[0]] = pd.to_datetime(df_observacoes[df_observacoes.columns[0]])
    df_predicoes[df_predicoes.columns[0]] = pd.to_datetime(df_predicoes[df_predicoes.columns[0]])

    # Criando Series a partir dos DataFrames
    observacoes = pd.Series(df_observacoes[df_observacoes.columns[1]].values)
    observacoes.reset_index()
    observacoes.index = df_observacoes[df_observacoes.columns[0]]

    predicoes = pd.Series(df_predicoes[df_predicoes.columns[1]].values)
    predicoes.reset_index()
    predicoes.index = df_predicoes[df_predicoes.columns[0]]

    # Padronizando index dos Series como "yyy-MM-dd"
    observacoes.index = observacoes.index.to_period("D")
    predicoes.index = predicoes.index.to_period("D")

    # Criando ndarray contendo apenas as observações reais para comparar com as predições
    y_test = observacoes.iloc[len(observacoes) - len(predicoes):len(observacoes)]

    ax = observacoes.plot(label='Observado', marker="o")
    predicoes.plot(ax=ax, label='Previsto', color="r", marker="o", alpha=.7)

    plt.savefig(PATH_METRICAS + '/' + nome_serie_temporal + '.png')
    plt.close()

    explained_variance = metrics.explained_variance_score(y_test, predicoes.values)
    mean_absolute_error = metrics.mean_absolute_error(y_test, predicoes.values)
    mse = metrics.mean_squared_error(y_test, predicoes.values)
    mean_squared_log_error = metrics.mean_squared_log_error(y_test, predicoes.values)
    r2 = metrics.r2_score(y_test, predicoes.values)

    # print('explained_variance: ', round(explained_variance, 4))
    # print('mean_squared_log_error: ', round(mean_squared_log_error, 4))

    return {
        "imagem": arquivo_para_base64(PATH_METRICAS + '/' + nome_serie_temporal + '.png'),
        "metricas": [
            {
                "metrica": "MSE",
                "valor": round(mse, 4)
            },
            {
                "metrica": "RMSE",
                "valor": round(np.sqrt(mse), 4)
            },
            {
                "metrica": "MAE",
                "valor": round(mean_absolute_error, 4)
            },
            {
                "metrica": "R2",
                "valor": round(r2, 4)
            }
        ]
    }
