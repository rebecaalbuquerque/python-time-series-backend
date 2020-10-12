import base64
import os
import shutil
from itertools import groupby
from os import listdir
from os.path import isfile, join


def arquivo_para_base64(path):
    data = open(path, "rb").read()
    return base64.b64encode(data).decode('ascii')


def lista_arquivos_do_diretorio(path):
    arquivos_no_diretorio = [f for f in listdir(path) if isfile(join(path, f))]
    arquivos_com_path = []
    result = []

    for file in arquivos_no_diretorio:
        arquivos_com_path.append(
            {
                "nome": file.split(".")[0],
                "path": path + "/" + file
            }
        )

    for k, v in groupby(arquivos_com_path, key=lambda x: x['nome']):
        d = {"nome": k}

        for p in [d['path'] for d in list(v)]:
            if p.endswith(".csv"):
                d["csv"] = p
            else:
                d["imagem"] = p

        result.append(d)

    return result


def limpar_diretorio(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
