import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR

path = r"C:\Users\bebec\Downloads\teste tcc\dados1\produtos.csv"

produtos_csv = pd.read_csv(path, sep=",")

"""
    Deduzindo que todas as series do csv tem o mesmo tamanho e que existe uma coluna "date"
"""

quantidade_series = produtos_csv.shape[0] / produtos_csv["index"].unique().size
produtos_csvs = np.array_split(produtos_csv, quantidade_series)

models = [
    ('LR', LinearRegression()),
    ('NN', MLPRegressor(solver='lbfgs')),
    ('KNN', KNeighborsRegressor()),
    ('RF', RandomForestRegressor(n_estimators=10)),
    ('SVR', SVR(gamma='auto'))
]

dict_predict_models = {
    "LR": [],
    "NN": [],
    "KNN": [],
    "RF": [],
    "SVR": []
}

for produto in produtos_csvs:
    produto["index"] = pd.to_datetime(produto["index"])
    produto = produto.set_index("index")

    data_sales = produto[["valor"]]

    X_train = data_sales[:'2020-09-09']
    y_train = data_sales.loc[:'2020-09-09', 'valor']

    X_test = data_sales['2020-09-10':]
    y_test = data_sales.loc['2020-09-10':, 'valor']

    # Evaluate each model in turn
    results_cross_validation = []
    names = []
    dataframes_preds = []

    for name, model in models:
        # print("########## " + name + " ##########")

        # TimeSeries Cross validation
        tscv = TimeSeriesSplit(n_splits=10)

        # Retorna o score pra cada rodada do cross validation (que no caso foram 10)
        cross_validation_score = cross_val_score(model, X_train, y_train, cv=tscv, scoring='r2')

        results_cross_validation.append(cross_validation_score)
        names.append(name)

        # print(">> Accuracy (cross validation score): ")
        # print("Mean: ", round(cross_validation_score.mean(), 4))
        # print("STD: ", round(cross_validation_score.std(), 4))

        y_true = y_test.values
        y_pred = model.fit(X_train, y_train).predict(X_test)

        dataframe_pred = pd.DataFrame({"valor": y_pred})

        dataframe_pred["item_nbr"] = produto.tail(X_test.size)["item_nbr"].values
        dataframe_pred["item"] = produto.tail(X_test.size)["item"].values
        dataframe_pred["categoria"] = produto.tail(X_test.size)["categoria"].values

        dataframe_pred["index"] = pd.to_datetime(y_test.index)
        dataframe_pred = dataframe_pred.set_index("index")

        dataframes_preds.append(dataframe_pred)

        dict_predict_models[name].append(dataframe_pred)

        model_fit = model.fit(X_train, y_train)
        # regression_results(y_true, y_pred)

for key, value in dict_predict_models.items():
    predictions = pd.concat(value)
    predictions["valor"] = predictions["valor"].round(decimals=14)
    predictions["categoria"] = predictions["categoria"].str.strip()
    predictions["item"] = predictions["item"].str.strip()
    predictions.to_csv(r"C:\Users\bebec\Downloads\teste tcc\dados1\predicoes_" + key + ".csv")
