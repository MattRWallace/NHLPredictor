import dateutil.parser as parser
import numpy as np
import pandas as pd

from nhlpy import NHLClient
from pickle import load

from databuilder.data_builder import DataBuilder
from loggingconfig.logging_config import LoggingConfig
from model.average_player_summarizer import AveragePlayerSummarizer
from model.home_or_away import HomeOrAway
from model.utility import Utility

logger = LoggingConfig.get_logger(__name__)

class Predictor:
    
    @staticmethod
    def predict(
        model_file_name: str,
        date: str = None
    ):
        summarizer = AveragePlayerSummarizer()
        client = NHLClient()
        Predictor.linear_regression(summarizer, model_file_name, client, date)

    @staticmethod
    def linear_regression(summarizer, model_file_name, client, date):
        data = []
        results_table = [["Game", "Predicted", "Actual"]]
        
        with open(model_file_name, "rb") as file:
            model = load(file)
        
        schedule = Predictor.get_todays_games(client, date)
        if (int(schedule["numberOfGames"]) <= 0):
            logger.warning("No games on the schedule for chosen date.")
            return
        
        for game in schedule["games"]:
            logger.info(f"Processing game. ID: '{game["id"]}'.")
            box_score = client.game_center.boxscore(game["id"])
            data.append(DataBuilder.process_game(game, box_score, summarizer))
            
        df = pd.DataFrame(data)
        df.columns = summarizer.get_headers()
        targetsColumnName = df.columns[len(df.columns)-1]
        actuals = df[targetsColumnName].to_list()
        df.drop(targetsColumnName, axis=1, inplace=True)
        data_pred = model.predict(df)
        
        if len(data_pred) != len(actuals):
            logger.error("Predictions and actual values vary in length")
            return
        
        for i in range(len(data_pred)):
            home_team = schedule["games"][i]["homeTeam"]["commonName"]["default"]
            away_team = schedule["games"][i]["awayTeam"]["commonName"]["default"]
            teams = f"{home_team} vs. {away_team}"
            prediction = HomeOrAway(np.rint(data_pred[i]).astype(int)).name
            actual = HomeOrAway(int(actuals[i])).name
            results_table.append([teams, prediction, actual])
            
        Utility.print_table(results_table)
        
    @staticmethod
    def get_todays_games(client, date):
        date = parser.parse(date)
        return client.schedule.daily_schedule(str(date)[:10])