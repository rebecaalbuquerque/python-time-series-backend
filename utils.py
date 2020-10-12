import base64
import os
import shutil
from itertools import groupby
from os import listdir
from os import path as os_path
from os.path import isfile, join


def arquivo_para_base64(path):
    data = open(path, "rb").read()
    return base64.b64encode(data).decode('ascii')


def lista_arquivos_do_diretorio(path):
    arquivos_no_diretorio = [f for f in listdir(path) if isfile(join(path, f))]
    result = []

    for index in range(0, len(arquivos_no_diretorio), 2):
        file_name = arquivos_no_diretorio[index].split(".")[0]

        result.append(
            {
                "nome": file_name,
                "csv": path + "/" + file_name + ".csv",
                "imagem": path + "/" + file_name + ".png"
            }
        )

    print(result)
    return result


def limpar_diretorio(path):

    if os_path.exists(path):
        print("limpar_diretorio >> true")

        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        print("limpar_diretorio >> false")
