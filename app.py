import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

from static.gerador_ts.constants import PATH_SERIES_TEMPORAIS_SINTETICAS, PATH_METRICAS
from static.gerador_ts.gerador import gerar
from utils import arquivo_para_base64, lista_arquivos_do_diretorio

app = Flask(__name__)
CORS(app)


@app.route('/seriesTemporaisSinteticas', methods=["GET"])
def gerar_series_temporais():
    gerar()

    response = []

    for arquivo in lista_arquivos_do_diretorio(PATH_SERIES_TEMPORAIS_SINTETICAS):
        ts = {
            "nome": arquivo["nome"],
            "csv": arquivo_para_base64(arquivo["csv"]),
            "imagem": arquivo_para_base64(arquivo["imagem"])
        }

        response.append(ts)

    return jsonify(response)


@app.route("/metricas", methods=["POST"])
def gerar_metricas():
    file = request.files['dadosReais']

    with open(PATH_METRICAS + "/aaa.csv", "wb") as temp_file:
        temp_file.write(file.read())


    print()
    return jsonify({"message": "ok"})


if __name__ == '__main__':
    app.run()
