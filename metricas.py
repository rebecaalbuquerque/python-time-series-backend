from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn.metrics as metrics

from constants import PATH_METRICAS, PATH_METRICAS_FILTRADAS, NOME_COLUNA_INDEX, NOME_COLUNA_VALOR, \
    NOME_COLUNA_CATEGORIA, NOME_COLUNA_ITEM
from utils import arquivo_para_base64

"""
    df_observacoes = df com N series temporais
    df_predicoes = df com predicoes das N series temporais
"""


def gerar_metricas_e_plot_predicoes(nome_modelo, df_observacoes, df_predicoes):
    # limpar_diretorio(PATH_METRICAS)

    df_predicoes.to_csv(PATH_METRICAS + '/' + nome_modelo + '@predicoes.csv', index=False)

    quantidade_series = df_observacoes.shape[0] / df_observacoes[NOME_COLUNA_INDEX].unique().size

    array_df_observacoes = np.array_split(df_observacoes, quantidade_series)
    array_df_predicoes = np.array_split(df_predicoes, quantidade_series)

    df_observacoes_soma = _somar_dataframes(NOME_COLUNA_INDEX, NOME_COLUNA_VALOR, array_df_observacoes)
    df_predicoes_soma = _somar_dataframes(NOME_COLUNA_INDEX, NOME_COLUNA_VALOR, array_df_predicoes)

    # Criando Series a partir dos DataFrames
    observacoes = pd.Series(df_observacoes_soma[NOME_COLUNA_VALOR].values)
    observacoes.reset_index()
    observacoes.index = pd.to_datetime(df_observacoes_soma[NOME_COLUNA_INDEX])

    predicoes = pd.Series(df_predicoes_soma[NOME_COLUNA_VALOR].values)
    predicoes.reset_index()
    predicoes.index = pd.to_datetime(df_predicoes_soma[NOME_COLUNA_INDEX])

    soma_observacoes = observacoes.iloc[(observacoes.size - predicoes.size):].sum()
    soma_predicoes = predicoes.sum()

    observacoes_ruptura_series = observacoes.iloc[(observacoes.size - predicoes.size):]
    predicoes_ruptura_series = predicoes

    # Criando ndarray contendo apenas as observações reais para comparar com as predições
    y_test = observacoes.iloc[len(observacoes) - len(predicoes):len(observacoes)]

    ax = observacoes.plot(figsize=(15, 8), label='Observado', marker="o")
    predicoes.index = observacoes.tail(predicoes.size).index
    predicoes.plot(figsize=(15, 8), ax=ax, label='Previsto', color="r", marker="o", alpha=.7)
    ax.set_xlabel("")

    plt.savefig(PATH_METRICAS + '/' + nome_modelo + '.png', bbox_inches='tight')
    plt.close()

    mean_absolute_error = metrics.mean_absolute_error(y_test, predicoes.values)
    mse = metrics.mean_squared_error(y_test, predicoes.values)
    r2 = metrics.r2_score(y_test, predicoes.values)

    soma_previsoes_abaixo = 0

    for item_observacoes, item_predicoes in zip(observacoes_ruptura_series, predicoes_ruptura_series):
        if item_predicoes < item_observacoes:
            soma_previsoes_abaixo += 1

    excesso = (soma_predicoes - soma_observacoes) / soma_observacoes
    ruptura = soma_previsoes_abaixo / predicoes.size

    return {
            "imagem": arquivo_para_base64(PATH_METRICAS + '/' + nome_modelo + '.png'),
            "metricas": [
                {"metrica": "MSE", "valor": str(round(mse, 4))},
                {"metrica": "RMSE", "valor": str(round(np.sqrt(mse), 4))},
                {"metrica": "MAE", "valor": str(round(mean_absolute_error, 4))},
                {"metrica": "R2", "valor": str(round(r2, 4))},
                {"metrica": "EXCESSO", "valor": str(round(excesso * 100, 3)) + "%"},
                {"metrica": "RUPTURA", "valor": str(round(ruptura * 100, 3)) + "%"}
            ]
        }


"""
    modelo é sempre diferente de None
"""


def gerar_imagem_dados_observado_e_predicoes(modelo, categoria, item):

    df_observacoes = _buscar_dataframe_dados_reais()

    # Predicoes apenas do modelo selecionado
    df_predicao = _buscar_dataframe_predicao(modelo)

    # Filtra "categoria" e "item" apenas no csv do "modelo" escolhido, e soma todas as séries desse modelo
    df_observacoes = _filtrar_linhas_dataframe_por_categoria_e_item(df_observacoes, categoria, item)
    df_predicao = _filtrar_linhas_dataframe_por_categoria_e_item(df_predicao, categoria, item)

    # Configurando pd.Series
    observacoes = df_observacoes[NOME_COLUNA_VALOR]
    observacoes.reset_index()
    observacoes.index = pd.to_datetime(df_observacoes[NOME_COLUNA_INDEX])

    predicoes = df_predicao[NOME_COLUNA_VALOR]
    predicoes.reset_index()
    predicoes.index = pd.to_datetime(df_predicao[NOME_COLUNA_INDEX])

    # Gerando gráfico
    ax = observacoes.plot(figsize=(15, 8), label='Observado', marker="o")
    predicoes.plot(figsize=(15, 8), ax=ax, label='Previsto', color="r", marker="o", alpha=.7)
    ax.set_xlabel("")

    # Gerando imagem
    plt.savefig(PATH_METRICAS_FILTRADAS + '/result_' + modelo + '.png', bbox_inches='tight')
    plt.close()

    return arquivo_para_base64(PATH_METRICAS_FILTRADAS + '/result_' + modelo + '.png')


def _somar_dataframes(nome_coluna_index, nome_coluna_soma, array_dataframe):
    df_soma = pd.DataFrame()
    df_soma[nome_coluna_index] = array_dataframe[0][nome_coluna_index].unique()
    df_soma[nome_coluna_soma] = 0

    for df in array_dataframe:
        df = df.reset_index()
        df_soma[nome_coluna_soma] = df[nome_coluna_soma].fillna(0) + df_soma[nome_coluna_soma]

    return df_soma


def _filtrar_linhas_dataframe_por_categoria_e_item(df, categoria, item):

    if categoria is None:
        quantidade_series = df.shape[0] / df[NOME_COLUNA_INDEX].unique().size
        array_df = np.array_split(df, quantidade_series)
        df_soma = _somar_dataframes(NOME_COLUNA_INDEX, NOME_COLUNA_VALOR, array_df)
        result = df_soma
    else:

        if item is not None:
            # Como filtro por uma categoria e um item, acaba resultando em apenas uma serie temporal de um item
            result = df[(df[NOME_COLUNA_CATEGORIA] == categoria) & (df[NOME_COLUNA_ITEM] == item)]
        else:
            # Soma todas as linhas da categoria selecionada pra ficar so uma serie
            df_filtrado = df[(df[NOME_COLUNA_CATEGORIA] == categoria)]

            quantidade_series = df_filtrado.shape[0] / df_filtrado[NOME_COLUNA_INDEX].unique().size
            array_df = np.array_split(df_filtrado, quantidade_series)

            df_soma = _somar_dataframes(NOME_COLUNA_INDEX, NOME_COLUNA_VALOR, array_df)
            result = df_soma

    return result


def _buscar_dataframe_dados_reais():
    for arquivo in [f for f in listdir(PATH_METRICAS) if isfile(join(PATH_METRICAS, f))]:
        if ".png" not in arquivo and "@dadosReais" in arquivo:
            return pd.read_csv(PATH_METRICAS + "/" + arquivo)

    return pd.DataFrame()


def _buscar_dataframe_predicao(modelo):
    for arquivo in [f for f in listdir(PATH_METRICAS) if isfile(join(PATH_METRICAS, f))]:
        if ".png" not in arquivo and "@predicoes" in arquivo and modelo in arquivo:
            return pd.read_csv(PATH_METRICAS + "/" + arquivo)

    return pd.DataFrame()


def _buscar_lista_dataframes_predicao():
    result = []

    for arquivo in [f for f in listdir(PATH_METRICAS) if isfile(join(PATH_METRICAS, f))]:
        if ".png" not in arquivo and "@predicoes" in arquivo:
            result.append(pd.read_csv(PATH_METRICAS + "/" + arquivo))

    return result
