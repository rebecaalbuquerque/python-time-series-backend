from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn.metrics as metrics

from constants import PATH_METRICAS, PATH_METRICAS_FILTRADAS
from utils import arquivo_para_base64, limpar_diretorio


def gerar_metricas_e_plot_predicoes(nome_serie_temporal, df_observacoes, df_predicoes):
    # limpar_diretorio(PATH_METRICAS)

    # Setando index dos DataFrames como um DateTime
    # df_observacoes[df_observacoes.columns[0]] = pd.to_datetime(df_observacoes[df_observacoes.columns[0]])
    # df_predicoes[df_predicoes.columns[0]] = pd.to_datetime(df_predicoes[df_predicoes.columns[0]])

    df_observacoes.to_csv(PATH_METRICAS + '/' + nome_serie_temporal + '@dadosReais.csv', index=False)
    df_predicoes.to_csv(PATH_METRICAS + '/' + nome_serie_temporal + '@predicoes.csv', index=False)

    # Criando Series a partir dos DataFrames
    observacoes = pd.Series(df_observacoes[df_observacoes.columns[1]].values)
    observacoes.reset_index()
    observacoes.index = df_observacoes[df_observacoes.columns[0]]

    predicoes = pd.Series(df_predicoes[df_predicoes.columns[1]].values)
    predicoes.reset_index()
    predicoes.index = df_predicoes[df_predicoes.columns[0]]

    # Padronizando index dos Series como "yyy-MM-dd"
    # observacoes.index = observacoes.index.to_period("D")
    # predicoes.index = predicoes.index.to_period("D")

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


"""
    Se o filtro for "modelo" pega todos os .csv que tem o modelo igual ao modelo solicitado e soma a coluna "valor".
    Se o filtro for "categoria" pega todos os .csv, verifica quais tem a categoria desejada e soma a coluna "valor".
    Se o filtro for "item" pega todos os .csv, verifica quais tem o item desejado e soma a coluna "valor".
"""


def gerar_imagem_dados_observado_e_predicoes(tipo_filtro, valor_filtro):
    limpar_diretorio(PATH_METRICAS_FILTRADAS)
    bases = []
    bases_filtro = []

    for arquivo in [f for f in listdir(PATH_METRICAS) if isfile(join(PATH_METRICAS, f))]:
        if ".png" not in arquivo:
            nome = arquivo.split("-")

            if not any(dictionary['id'] == nome[0] for dictionary in bases):
                bases.append(
                    {
                        "id": nome[0],
                        "modelo": arquivo[arquivo.find("(") + 1:arquivo.find(")")],
                        "dadosReais": pd.read_csv(PATH_METRICAS + "/" + arquivo.split("@")[0] + "@dadosReais.csv"),
                        "predicoes": pd.read_csv(PATH_METRICAS + "/" + arquivo.split("@")[0] + "@predicoes.csv")
                    }
                )

    if tipo_filtro == "modelo":

        for base in bases:
            if base["modelo"] == valor_filtro:
                bases_filtro.append(base)

    elif tipo_filtro == "categoria":

        for base in bases:
            if valor_filtro in base["dadosReais"][tipo_filtro].unique():
                bases_filtro.append({
                    "dadosReais": base["dadosReais"][base["dadosReais"][tipo_filtro] == valor_filtro],
                    "predicoes": base["predicoes"][base["predicoes"][tipo_filtro] == valor_filtro]
                })

    else:
        for base in bases:
            if valor_filtro in base["dadosReais"][tipo_filtro].unique():
                bases_filtro.append({
                    "dadosReais": base["dadosReais"][base["dadosReais"][tipo_filtro] == valor_filtro],
                    "predicoes": base["predicoes"][base["predicoes"][tipo_filtro] == valor_filtro]
                })

    # Iniciando variavel que receberá a soma
    soma_observacoes = np.zeros(bases_filtro[0]["dadosReais"]["valor"].shape)
    soma_predicoes = np.zeros(bases_filtro[0]["predicoes"]["valor"].shape)

    # Realizando a soma
    for base_modelo in bases_filtro:
        soma_observacoes = base_modelo["dadosReais"]["valor"].fillna(0) + soma_observacoes
        soma_predicoes = base_modelo["predicoes"]["valor"].fillna(0) + soma_predicoes

    # Configurando pd.Series
    observacoes = pd.Series(soma_observacoes)
    observacoes.reset_index()
    observacoes.index = list(range(0, len(observacoes.index)))

    predicoes = pd.Series(soma_predicoes)
    predicoes.reset_index()
    predicoes.index = list(range(len(observacoes.index) - len(predicoes.index), len(observacoes.index)))

    # Gerando gráfico
    ax = observacoes.plot(label='Observado', marker="o")
    predicoes.plot(ax=ax, label='Previsto', color="r", marker="o", alpha=.7)

    # Gerando imagem
    plt.savefig(PATH_METRICAS_FILTRADAS + '/result.png')
    plt.close()

    return arquivo_para_base64(PATH_METRICAS_FILTRADAS + '/result.png')
