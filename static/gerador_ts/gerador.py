import json
from glob import glob
from random import randint
from random import uniform

import matplotlib.pyplot as plt
import pandas as pd


def _mean(l):
    return sum(l) / len(l)


def dependencia(data):
    # data = {}
    # data['dependencia'] = []
    # data['dependencia'] = {
    #     'minV': 50,
    #     'maxV': 100,
    #     'correlacao': 40,
    #     'tipoInicial': 'sazonal',
    #     'tipoDependencia': 'negativo',
    #     'n': 100,
    #     'aleatoriedade': 15,
    #     'elasticidade': {
    #         'porcentagem': 5,
    #         'pMin': 10,
    #         'pMax': 20,
    #         'vMin': 20,
    #         'vMax': 200,
    #         'aleatoriedadeDiaria': 4
    #     },
    #     'sazonal': {
    #         's': 7,
    #         'diasDsazonalidade': 1,
    #         'picoMax': 40,
    #         'picoMin': 15,
    #         'baixoMax': 10,
    #         'baixoMin': 5
    #     }
    # }
    #
    # with open('config.txt', 'w') as outfile:
    #     json.dump(data, outfile)

    # with open('config.txt') as json_file:
    #     data = json.load(json_file)

    tipoInicial = data["tipoInicial"]
    tipoDependencia = data["tipoDependencia"]

    n = data['n']

    minV = data['minV']  # venda minima inicial
    maxV = data['maxV']  # venda maxima inicial

    correlacao = data['correlacao']  # em porcentagem

    aleatoriedade = data['variacaoDiaria']  # em porcentagem

    vendas = []
    vendas_puras = []
    dias = []
    vendasDir = []

    if tipoInicial == "elasticidade":
        vendasE, precoE = elasticidade(n,
                                       data['elasticidade']['variacao'],
                                       data['elasticidade']['pMin'],
                                       data['elasticidade']['pMax'],
                                       data['elasticidade']['vMin'],
                                       data['elasticidade']['vMax'],
                                       data['elasticidade']['aleatoriedadeDiaria'],
                                       data['elasticidade']['duracaoVenda'])
    elif tipoInicial == "sazonal":
        vendasE = sazonal(n,
                          data['sazonal']['s'],
                          data['sazonal']['diasDsazonalidade'],
                          data['sazonal']['picoMax'],
                          data['sazonal']['picoMin'],
                          data['sazonal']['baixoMax'],
                          data['sazonal']['baixoMin'])
        precoE = 0

    for i in range(n):
        sinalRandomico = 1
        if randint(2, 3) % 2 == 0:
            sinalRandomico = -1

        dias.append(i + 1)
        if i == 0:
            primeiroValor = ((maxV - minV) * randint(0, 100) / 100) + minV
            vendas.append(primeiroValor)
            vendas_puras.append(primeiroValor)
            vendasDir.append(primeiroValor)
        else:
            # fazer diretamente ou inversamente proporcional e depois aplicar o jitter
            aleatoriedade_round = (1 + (sinalRandomico * randint(0, 100) * aleatoriedade / 10000))
            vendas_puras.append(vendas_puras[i - 1] * aleatoriedade_round)
            A = vendas[i - 1] * aleatoriedade_round
            if tipoDependencia == "negativo":
                venda = (vendas[i - 1] * vendasE[i - 1] / vendasE[i])
            elif tipoDependencia == "positivo":
                venda = (vendas[i - 1] * vendasE[i] / vendasE[i - 1])

            vendas.append(venda)
            vendasDir.append(venda)

    mediaVP = _mean(vendas_puras)
    print(mediaVP)
    mediaV = _mean(vendas)
    print(mediaV)

    for i in range(n):
        if tipoInicial == "sazonal":
            vendas[i] = (vendas[i] * (correlacao / 100)) + (
                        (vendas_puras[i] * (mediaV / mediaVP)) * (abs(correlacao - 100) / 100))
        else:
            vendas[i] = (vendas[i] * (correlacao / 100)) + (vendas_puras[i] * (abs(correlacao - 100) / 100))

    # plt.subplot(4, 1, 1)
    # plt.plot(dias, vendasE)
    # plt.title("elasticidade")
    # plt.subplot(4, 1, 2)
    # plt.plot(dias, vendas_puras)
    # plt.title("venda pura")
    # plt.subplot(4, 1, 3)
    # plt.plot(dias, vendasDir)
    # plt.title("dir prop")
    # plt.subplot(4, 1, 4)
    # plt.plot(dias, vendas)
    # plt.title("dependencia")

    plt.subplot(2, 1, 1)
    plt.plot(dias, vendasE)
    plt.title(tipoInicial)
    plt.subplot(2, 1, 2)
    plt.plot(dias, vendas)
    plt.title("produto dependente")

    # plt.savefig("dependencia")
    # plt.show()
    plt.close()

    return (vendas, vendasE, precoE)


def sazonal(n, s, diasDsazonalidade, picoMax, picoMin, baixoMax, baixoMin):
    dias = []
    vendas = []

    ds = 0

    for i in range(n):
        dias.append(i + 1)
        if (i + 1) % s == 0:
            ds = diasDsazonalidade

        if ds > 0:
            venda = ((picoMax - picoMin) * randint(0, 100) / 100) + picoMin
        else:
            venda = ((baixoMax - baixoMin) * randint(0, 100) / 100) + baixoMin

        ds = ds - 1
        vendas.append(venda)
    return vendas


def elasticidade(n, porcentagem, pMin, pMax, vMin, vMax, aleatoriedadeDiaria, duracaoVenda):
    jitter = ((vMin + vMax) / 2) * aleatoriedadeDiaria / 100

    dias = []
    vendas = []
    precos = []

    precoAtual = uniform(pMin, pMax)
    vendaAtual = randint(vMin, vMax)
    diasAtuais = randint(1, int(n * duracaoVenda / 100))

    for i in range(n):
        dias.append(i + 1)

        sinal = 1
        if randint(2, 3) % 2 == 0:
            sinal = -1

        if diasAtuais == 0:
            precoAntigo = precoAtual
            vendaAntigo = vendaAtual
            precoAtual = uniform(pMin, pMax)
            diasAtuais = randint(1, int(n / 3))
            vendaAtual = (vendaAntigo * precoAntigo / precoAtual)
            vendaAtual = vendaAtual + sinal * randint(0, int(
                vendaAtual * porcentagem / 100))  # tem um range de 5% pra cima e pra baixo com base na aleatoriedade para nao ficar exatamente inversamente proporcional

        randomicJitter = randint(0, 100) * sinal * jitter / 100

        precos.append(precoAtual)
        venda = vendaAtual + randomicJitter

        diasAtuais = diasAtuais - 1

        vendas.append(venda)

    return vendas, precos


def gerar():
    with open('static/gerador_ts/config.txt') as json_file:
        item = json.load(json_file)

    for item in item['lista']:
        print(item)

        if item['tipoSerie'] == "sazonal":
            dic = {}

            for i in range(item['qtdGerados']):
                vendas_sazonais = sazonal(item['n'], item['s'], item['diasDsazonalidade'], item['picoMax'],
                                          item['picoMin'], item['baixoMax'], item['baixoMin'])

                dic.update(
                    {
                        'ts': range(len(vendas_sazonais)),
                        'venda-' + str(i): vendas_sazonais
                    }
                )

                plt.plot(range(len(vendas_sazonais)), vendas_sazonais)
                plt.title("Sazonal ")
                plt.savefig('static/gerador_ts/arquivos/sazonal' + str(i) + '.png')
                # plt.show()
                plt.close()
                pd.DataFrame(dic).to_csv('static/gerador_ts/arquivos/sazonal' + str(i) + '.csv', index=False)

        elif item['tipoSerie'] == "elasticidade":
            dic = {}
            for i in range(item['qtdGerados']):
                vendas, precos = elasticidade(item['n'],
                                              item['variacao'],
                                              item['pMin'],
                                              item['pMax'],
                                              item['vMin'],
                                              item['vMax'],
                                              item['aleatoriedadeDiaria'],
                                              item['duracaoVenda'])

                plt.subplot(2, 1, 1)
                plt.plot(range(len(precos)), vendas)
                plt.title("vendas")
                plt.subplot(2, 1, 2)
                plt.plot(range(len(precos)), precos)
                plt.title("precos")
                # plt.show()
                plt.close()

                dic.update({'venda-' + str(i): vendas, 'preco-' + str(i): precos})

            files = glob('static/gerador_ts/arquivos/elasticidade*')
            pd.DataFrame(dic).to_csv('static/gerador_ts/arquivos/elasticidade' + str(len(files)) + '.csv', index=False)

        elif item['tipoSerie'] == "dependencia":
            dic = {}
            for i in range(item['qtdGerados']):
                vendaDep, vendasE, precoE = dependencia(item)

                dic.update({'venda-item-Dep-' + str(i): vendaDep, 'venda-item-anterior-' + str(i): vendaDep,
                            'preco-item-anterior-' + str(i): precoE})

            files = glob('static/gerador_ts/arquivos/dependencia*')
            pd.DataFrame(dic).to_csv('static/gerador_ts/arquivos/dependencia' + str(len(files)) + '.csv', index=False)
