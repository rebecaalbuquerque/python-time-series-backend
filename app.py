import base64
from io import StringIO

import pandas as pd
from flask import Flask, jsonify, request, url_for, render_template
from flask_cors import CORS

from constants import PATH_SERIES_TEMPORAIS_SINTETICAS
from gerador import gerar
from metricas import gerar_metricas_e_plot_predicoes
from utils import arquivo_para_base64, lista_arquivos_do_diretorio

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


@app.route("/metricas", methods=["POST"])
def gerar_metricas():

    body = request.get_json()
    response = []

    for index, item in enumerate(body):

        csv_dados_reais_64_decode = base64.decodebytes(item["dadosReais"].split("base64")[1].encode())
        csv_predicoes_64_decode = base64.decodebytes(item["predicoes"].split("base64")[1].encode())

        df_dados_reais = pd.read_csv(StringIO(str(csv_dados_reais_64_decode, 'utf-8')))
        df_predicoes = pd.read_csv(StringIO(str(csv_predicoes_64_decode, 'utf-8')))

        metricas_e_plot = gerar_metricas_e_plot_predicoes(
            item["dadosReaisArquivo"].replace(".csv", "") + " " + str(index) + "(" + item["nomeModelo"] + ")",
            df_dados_reais,
            df_predicoes
        )

        response.append(
            {
                "nome": item["dadosReaisArquivo"].replace(".csv", "") + " (" + item["nomeModelo"] + ")",
                "imagem": metricas_e_plot["imagem"],
                "metricas": metricas_e_plot["metricas"]
            }
        )

    return jsonify(response)


if __name__ == '__main__':
    app.run()
