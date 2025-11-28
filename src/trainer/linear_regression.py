from pickle import dump

import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


class TrainLinearRegression:

    @staticmethod
    def train(output, data_files):
        # Dump all lines when printing pandas data. TODO: Delete this.
        # pd.set_option("display.max_rows", None, "display.max_columns", None)

        train = pd.concat(map(pd.read_csv, data_files), ignore_index=True)
        targetsColumnName = train.columns[len(train.columns)-1]
        train_targets = train[targetsColumnName].to_list()
        train.drop(targetsColumnName, axis=1, inplace=True)

        test = pd.read_csv("currentSeason.csv")
        test_targets = test[targetsColumnName].to_list()
        test.drop(targetsColumnName, axis=1, inplace=True)
        
        # create LR model
        model = LinearRegression()

        # Fit
        model.fit(train, train_targets)

        # TODO: Clean up the presentation of stats here.

        # r-squared
        train_pred = model.predict(train)
        r_squared = r2_score(train_targets, train_pred)
        print("R-squared: ", r_squared)

        # P-Values
        x_intercept = sm.add_constant(train)
        model_sm = sm.OLS(train_targets, x_intercept).fit()
        print("P-Values: ", model_sm.pvalues)
        
        print("Mean squared error: %.2f" % mean_squared_error(train_targets, train_pred))

        test_pred = model.predict(test)
        r_squared = r2_score(test_targets, test_pred)
        print("R-squared: ", r_squared)

        # P-Values
        x_intercept = sm.add_constant(test)
        model_sm = sm.OLS(test_targets, x_intercept).fit()
        print("P-Values: ", model_sm.pvalues)
        
        print("Mean squared error: %.2f" % mean_squared_error(test_targets, test_pred))

        # Coefficients
        print("Coef: ", model.coef_)
        print("Intercept: ", model.intercept_)

        if output is None:
            output = "LinearRegressionModel.pkl"
        with open(output, "wb") as file:
            dump(model, file, protocol=5)