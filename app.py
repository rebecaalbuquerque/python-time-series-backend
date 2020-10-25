import base64
from io import StringIO

import pandas as pd
from flask import Flask, jsonify, request, url_for, render_template
from flask_cors import CORS

from constants import PATH_SERIES_TEMPORAIS_SINTETICAS, PATH_METRICAS
from gerador import gerar
from metricas import gerar_metricas_e_plot_predicoes, gerar_imagem_dados_observado_e_predicoes
from utils import arquivo_para_base64, lista_arquivos_do_diretorio, limpar_diretorio

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def root():
    links = []

    for rule in app.url_map.iter_rules():
        if "static" not in rule.endpoint and "root" not in rule.endpoint:

            for method in rule.methods:

                if method != "OPTIONS" and method != "HEAD":

                    if method != "GET":
                        url = "/"
                    else:
                        url = url_for(rule.endpoint, **(rule.defaults or {}))

                    links.append((url, "[" + method + "]  " + rule.endpoint))

    return render_template("all_links.html", links=links)


@app.route('/seriesTemporaisSinteticas', methods=["GET"])
def gerar_series_temporais_sinteticas():
    gerar()

    response = []

    for arquivo in lista_arquivos_do_diretorio(PATH_SERIES_TEMPORAIS_SINTETICAS):
        print(arquivo)
        ts = {
            "nome": arquivo["nome"],
            "csv": arquivo_para_base64(arquivo["csv"]),
            "imagem": arquivo_para_base64(arquivo["imagem"])
        }

        response.append(ts)

    return jsonify(response)


"""
    REQUEST
    [
        {
            "nomeModelo": "nome_modelo_1",
            "dadosReais": "string base64 csv",
            "dadosReaisArquivo": "nome_arquivo_1.csv",
            "predicoes": "string base64 csv"
        },
        { 
            "nomeModelo": "nome_modelo_2",
            "dadosReais": "string base64 csv",
            "dadosReaisArquivo": "nome_arquivo_2.csv",
            "predicoes": "string base64 csv"
        }
    ]
    
    RESPONSE
    {
        "filtros": {
            "categorias": ["Bebida", "Frios"],
            "itens": ["Heineken", "Queijo Mussarela Sadia", "Presunto Sadia", "Skol", "Brahma", "Mortadela Sadia"],
            "modelos": ["KNN", "ARIMA", "SARIMA"]
        },
        "responseMetricas": [
            {
                "nome": "nome_arquivo_1 (nome_modelo_1)",
                "imagem": "base64 string",
                "metricas": [
                    "metrica": "MSE",
                    "valor": 2255.93
                ]
            },
            {
                "nome": "nome_arquivo_2 (nome_modelo_2)",
                "imagem": "base64 string",
                "metricas": [
                    "metrica": "MSE",
                    "valor": 2255.93
                ]
            }
        ]
    }
"""


@app.route("/metricas", methods=["POST"])
def gerar_metricas():
    limpar_diretorio(PATH_METRICAS)
    body = request.get_json()

    response_metricas = []
    response_modelos = []
    response_categorias = []
    response_itens = []

    for index, item in enumerate(body):
        response_modelos.append(item["nomeModelo"])

        csv_dados_reais_64_decode = base64.decodebytes(item["dadosReais"].split("base64")[1].encode())
        csv_predicoes_64_decode = base64.decodebytes(item["predicoes"].split("base64")[1].encode())

        df_dados_reais = pd.read_csv(StringIO(str(csv_dados_reais_64_decode, 'utf-8')))
        df_predicoes = pd.read_csv(StringIO(str(csv_predicoes_64_decode, 'utf-8')))

        if "categoria" in df_predicoes:
            response_categorias.extend(df_predicoes["categoria"].unique().tolist())

        if "item" in df_predicoes:
            response_itens.extend(df_predicoes["item"].unique().tolist())

        metricas_e_plot = gerar_metricas_e_plot_predicoes(
            str(index) + " - " + item["dadosReaisArquivo"].replace(".csv", "") + "(" + item["nomeModelo"] + ")",
            df_dados_reais,
            df_predicoes
        )

        response_metricas.append(
            {
                "nome": item["dadosReaisArquivo"].replace(".csv", "") + " (" + item["nomeModelo"] + ")",
                "imagem": metricas_e_plot["imagem"],
                "metricas": metricas_e_plot["metricas"]
            }
        )

    response = {
        "responseMetricas": response_metricas,
        "filtros": {
            "modelos": list(dict.fromkeys(response_modelos)),
            "categorias": list(dict.fromkeys(response_categorias)),
            "itens": list(dict.fromkeys(response_itens))
        }
    }

    return jsonify(response)


"""
    
    REQUEST
    {
        "filtro": {
            "tipo": "modelo",
            "valor": "KNN"    
        }
    }
    
    RESPONSE
    {
        "imagem": "base 64 string"
    }
    
"""


@app.route("/metricasFiltradas", methods=["POST"])
def gerar_metricas_filtradas():
    body = request.get_json()

    # # se não tiver (csv dadosReais ou csv predicoes) ou se não tiver nenhum parametro => retornar corpo vazio
    # # if "dadosReais" not in body \
    # #         or ("dadosReais" in body and (body["dadosReais"] is None)) \
    # #         or "predicoes" not in body \
    # #         or ("predicoes" in body and (body["predicoes"] is None)) \
    # #         or ("modelo" not in body and "categoria" not in body and "item" not in body):
    # #     return jsonify({})
    #
    # # se não tiver N parametros => filtrar so com os parametros disponíveis
    # for key, value in dict(body).items():
    #     if value is None:
    #         del body[key]
    #
    # # se não tiver "modelo", mostra todas as séries temporais. caso contrário mostra so as series do modelo selecionado
    #
    # csv_dados_reais_64_decode = base64.decodebytes(body["dadosReais"].encode())
    # csv_predicoes_64_decode = base64.decodebytes(body["predicoes"].encode())
    #
    # df_dados_reais = pd.read_csv(StringIO(str(csv_dados_reais_64_decode, 'utf-8')))
    # df_predicoes = pd.read_csv(StringIO(str(csv_predicoes_64_decode, 'utf-8')))
    #
    # del body["dadosReais"]
    # del body["predicoes"]
    #
    # metricas_e_plot = gerar_metricas_e_plot_predicoes(
    #     "modelo x",
    #     df_dados_reais,
    #     df_predicoes,
    #     body
    # )

    if "filtro" not in body:
        return jsonify({"mensagem": "Objeto 'filtro' não encontrado."}), 400

    elif body["filtro"]["tipo"] == "modelo" \
            or body["filtro"]["tipo"] == "categoria" \
            or body["filtro"]["tipo"] == "item":
        return jsonify(
            {
                "imagem": gerar_imagem_dados_observado_e_predicoes(body["filtro"]["tipo"], body["filtro"]["valor"])
            }
        )

    else:
        return jsonify({"mensagem": "Filtro inexistente."}), 400


if __name__ == '__main__':
    app.run()
