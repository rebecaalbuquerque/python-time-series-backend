import base64
from io import StringIO

import pandas as pd
from flask import Flask, jsonify, request, url_for, render_template
from flask_cors import CORS

from constants import PATH_SERIES_TEMPORAIS_SINTETICAS, PATH_METRICAS, PATH_METRICAS_FILTRADAS, NOME_COLUNA_CATEGORIA, \
    NOME_COLUNA_ITEM
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
    
    NOVA REQUEST
    {
        "dadosReais": "string base64 csv",
        "dadosReaisArquivo": "nome_arquivo_2.csv",
        "predicoes": [
            {
                "nomeModelo": "nome_modelo_1",
                "predicao": "string base64 csv"
            },
            { 
                "nomeModelo": "nome_modelo_2",
                "predicao": "string base64 csv"
            }
        ]
    }
    
    RESPONSE
    {
        "filtros": {
            "categorias": [
                {
                    "itens": [
                        "QUEIJO MUSSARELA FATIADO KG",
                        "FRANGO RESF.REGINA KG"
                    ],
                    "nome": "FRIOS"
                },
                {
                    "itens": [
                        "REFRIG.COCA COLA 350ML LT",
                        "REFRIG.COCA COLA 2L PET"
                    ],
                    "nome": "BEBIDAS"
                }
            ],
            "modelos": [
                "KNN",
                "LR"
            ]
        },
        "responseMetricasPorModelo": [
            {
                "nome": "nome_modelo_1",
                "imagem": "base64 string",
                "metricas": [
                    "metrica": "MSE",
                    "valor": 2255.93
                ]
            },
            {
                "nome": "nome_modelo_2",
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

    if "base64" in body["dadosReais"]:
        csv_dados_reais_64_decode = base64.decodebytes(body["dadosReais"].split("base64")[1].encode())
    else:
        csv_dados_reais_64_decode = base64.decodebytes(body["dadosReais"].encode())

    df_dados_reais = pd.read_csv(StringIO(str(csv_dados_reais_64_decode, 'utf-8')))

    df_dados_reais[NOME_COLUNA_CATEGORIA] = df_dados_reais[NOME_COLUNA_CATEGORIA].str.strip()
    df_dados_reais[NOME_COLUNA_ITEM] = df_dados_reais[NOME_COLUNA_ITEM].str.strip()

    df_dados_reais.to_csv(
        PATH_METRICAS +
        '/' +
        body["dadosReaisArquivo"].replace(".csv", "") + '@dadosReais.csv', index=False
    )

    for categoria in df_dados_reais[NOME_COLUNA_CATEGORIA].unique():
        response_categorias.append({
            "nome": categoria,
            "itens": df_dados_reais[(df_dados_reais[NOME_COLUNA_CATEGORIA] == categoria)][NOME_COLUNA_ITEM].unique().tolist()
        })

    for index, item in enumerate(body["predicoes"]):
        response_modelos.append(item["nomeModelo"])

        if "base64" in item["predicao"]:
            csv_predicoes_64_decode = base64.decodebytes(item["predicao"].split("base64")[1].encode())
        else:
            csv_predicoes_64_decode = base64.decodebytes(item["predicao"].encode())

        # Criando um DF a partir do csv em base64
        df_predicoes = pd.read_csv(StringIO(str(csv_predicoes_64_decode, 'utf-8')))

        # Removendo espaços em branco no inicio e no final das colunas "categoria" e "item"
        df_predicoes[NOME_COLUNA_CATEGORIA] = df_predicoes[NOME_COLUNA_CATEGORIA].str.strip()
        df_predicoes[NOME_COLUNA_ITEM] = df_predicoes[NOME_COLUNA_ITEM].str.strip()

        # Gerando metricas da predicao
        metricas_e_plot = gerar_metricas_e_plot_predicoes(
            item["nomeModelo"],
            df_dados_reais,
            df_predicoes
        )

        response_metricas.append(
            {
                "nome": "predicoes" + " (" + item["nomeModelo"] + ")",
                "modelo": item["nomeModelo"],
                "imagem": metricas_e_plot["imagem"],
                "metricas": metricas_e_plot["metricas"]
            }
        )

    response = {
        "responseMetricasPorModelo": response_metricas,
        "filtros": {
            "modelos": list(dict.fromkeys(response_modelos)),
            "categorias": response_categorias
        }
    }

    return jsonify(response)


"""
    
    REQUEST
    {
        "primeiroFiltro": {
            "modelo": "",
            "categoria": "",
            "item": ""
        },
        "segundoFiltro": {
            "modelo": "",
            "categoria": "",
            "item": ""
        }
    }
    
    RESPONSE
    {
        "primeiroFiltroImagem": "base 64 string",
        "segundoFiltroImagem": "base 64 string"
    }
    
"""


@app.route("/metricasFiltradas", methods=["POST"])
def gerar_metricas_filtradas():
    limpar_diretorio(PATH_METRICAS_FILTRADAS)
    body = request.get_json()

    if "modelo" not in body["primeiroFiltro"]:
        return jsonify({"mensagem": "É necessário escolher pelo menos um 'modelo'."}), 400

    else:
        return jsonify(
            {
                "primeiroFiltroImagem": gerar_imagem_dados_observado_e_predicoes(
                    body["primeiroFiltro"]["modelo"], body["primeiroFiltro"][NOME_COLUNA_CATEGORIA], body["primeiroFiltro"][NOME_COLUNA_ITEM]
                ),
                "segundoFiltroImagem": gerar_imagem_dados_observado_e_predicoes(
                    body["segundoFiltro"]["modelo"], body["segundoFiltro"][NOME_COLUNA_CATEGORIA], body["segundoFiltro"][NOME_COLUNA_ITEM]
                )
            }
        )


if __name__ == '__main__':
    app.run()
