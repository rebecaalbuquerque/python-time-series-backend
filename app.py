from flask import Flask, jsonify
from flask_cors import CORS

from static.gerador_ts.gerador import gerar
from utils import arquivo_para_base64, lista_arquivos_do_diretorio

app = Flask(__name__)
CORS(app)


@app.route('/gerarSeriesTemporais')
def gerar_series_temporais():

    # gerar()

    response = []
    for arquivo in lista_arquivos_do_diretorio("static/gerador_ts/arquivos"):
        ts = {
            "nome": arquivo["nome"],
            "csv": arquivo_para_base64(arquivo["csv"]),
            "imagem": arquivo_para_base64(arquivo["imagem"])
        }

        response.append(ts)

    return jsonify(response)


if __name__ == '__main__':
    app.run()
