from pickle import dump

import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from model.summarizers import Summarizers
from shared.constants.database import Database as DB
from shared.execution_context import ExecutionContext
from shared.logging_config import LoggingConfig
from shared.utility import Utility as utl

logger = LoggingConfig.get_logger(__name__)
execution_context = ExecutionContext()

class TrainLinearRegression:
    
    @staticmethod
    def train_db():
        logger.info("Start of model training.")
        
        data = utl.get_pandas_tables(
            DB.players_table_name,
            DB.skater_stats_table_name,
            DB.goalie_stats_table_name,
            DB.games_table_name,
            DB.meta_table_name,
            path=execution_context.app_dir
        )

        summarizer = Summarizers.get_summarizer(execution_context.summarizer_type)
        game_data = summarizer.summarize(data)

        train, test = train_test_split(game_data, test_size=0.2)

        # TODO: This assumes that the last column is our winner column.  The
        # summarizer needs to either guarantee this or return them separately.
        targetsColumnName = train.columns[len(train.columns)-1]
        train_targets = train[targetsColumnName].to_list()
        train.drop(targetsColumnName, axis=1, inplace=True)
        targetsColumnName = test.columns[len(test.columns)-1]
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

        with open("LinearRegressionModel.pkl", "wb") as file:
            dump(model, file, protocol=5)

        logger.info("End of model training.")

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