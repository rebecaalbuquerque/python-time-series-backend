# TS Forecast Analysis
This is the web service of [TS Forecast Analysis](https://tsforecastanalysis.netlify.app/), a tool that combines several metrics to be able to evaluate numerous time series predictions, making it easier to view and analyze the metrics evaluation.

## Endpoints

#### /seriesTemporaisSinteticas
Generates 10 synthetic time series. For each time series generated there is a CSV file and its plot.

- GET

```
Response

[
    {
        "csv": "string base64 csv",
        "imagem": "string base64 imagem"
    },
    { 
        "csv": "string base64 csv",
        "imagem": "string base64 imagem"
    },
    { 
        "csv": "string base64 csv",
        "imagem": "string base64 imagem"
    }
]
```

#### /metricas
Returns the filters of models, categories and items of all imported data. It also returns a list of metrics generated for each prediction model.

- POST

```
Body

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
```

```
Response

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
```

#### /metricasFiltradas
Returns the images of the filters sent by the body.

-POST

```
Body

{
    "primeiroFiltro": {
        "modelo": "KNN",
        "categoria": "FRIOS",
        "item": "MARGARINA QUALY 500G"
    },
    "segundoFiltro": {
        "modelo": "LR",
        "categoria": "FRIOS",
        "item": "MARGARINA QUALY 500G"
    }
}
```

```
Response

{
    "primeiroFiltroImagem": "base 64 string",
    "segundoFiltroImagem": "base 64 string"
}
```

