from datetime import datetime, UTC, timedelta
import numpy as np
import pandas as pd

from nhlpy import NHLClient
from pickle import load
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

from databuilder.data_builder import DataBuilder
from loggingconfig.logging_config import LoggingConfig
from model.seasons import PastSeasons
from model.average_player_summarizer import AveragePlayerSummarizer
from model.utility import Utility

logger = LoggingConfig.get_logger(__name__)

class Predictor:
    
    @staticmethod
    def predict():
        summarizer = AveragePlayerSummarizer()
        client = NHLClient()
        Predictor.linear_regression(summarizer, client)

    @staticmethod
    def linear_regression(summarizer, client):
        data = []
        
        with open("AveragePlayersModel.pkl", "rb") as file:
            model = load(file)
        
        schedule = Predictor.get_todays_games(client)
        if (int(schedule["numberOfGames"]) <= 0):
            logger.warning("No games on the schedule for chosen date.")
            return
        
        for game in schedule["games"]:
            logger.info(f"Processing game. ID: '{game["id"]}'.")
            box_score = client.game_center.boxscore(game["id"])
            data.append(DataBuilder.process_game(game, box_score, summarizer))
            
        df = pd.DataFrame(data)
        targetsColumnName = df.columns[len(df.columns)-1]
        actual = df[targetsColumnName].to_list()
        df.drop(targetsColumnName, axis=1, inplace=True)
        
        
        data_pred = model.predict(df)
        
        if len(data_pred) != len(actual):
            logger.error("Predictions and actual values vary in length")
            return
        
        table = [["Predicted", "Actual"]]
        for i in range(len(data_pred)):
            table.append([str(np.rint(data_pred[i])), str(actual[i])])
            
        # for row in table:
        #     print(f"{row[0]}\t{row[1]}")
        Utility.print_table(table)
        
        
        # print(f"Predicted: '{data_pred}'.")
        # print(f"Actual: '{actual}'.")
        
        
    @staticmethod
    def get_todays_games(client):
        client = NHLClient()
        # TODO: Remove the offset
        #today = datetime.now(UTC).strftime('%Y-%m-%d')
        today = (datetime.now(UTC) - timedelta(1)).strftime('%Y-%m-%d')
        return client.schedule.daily_schedule(today)
    
Predictor.predict()
