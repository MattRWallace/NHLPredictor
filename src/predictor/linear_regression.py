from pickle import load

import dateutil.parser as parser
import numpy as np
import pandas as pd

from databuilder.data_builder import DataBuilder
from loggingconfig.logging_config import LoggingConfig
from model.home_or_away import HomeOrAway
from model.utility import Utility

logger = LoggingConfig.get_logger(__name__)

class PredictLinearRegression:
    
    @staticmethod
    def predict(summarizer, client, model_file_name, date, date_range):
        data = []
        results_table = [["Game", "Predicted", "Actual"]]
        with open(model_file_name, "rb") as file:
            model = load(file)

        if date is not None:
            games, number_of_games = (
                PredictLinearRegression.get_games_for_date(client, date)
            )
        elif date_range is not None:
            games, number_of_games = (
                PredictLinearRegression.get_games_for_date_range(client, date_range)
            )
        else:
            logger.error("No valid date option supplied")
            return

        if (number_of_games <= 0):
            logger.warning("No games on the schedule for chosen date(s).")
            return
        
        for game in games:
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
            home_team = games[i]["homeTeam"]["commonName"]["default"]
            away_team = games[i]["awayTeam"]["commonName"]["default"]
            teams = f"{home_team} vs. {away_team}"
            prediction = HomeOrAway(np.rint(data_pred[i]).astype(int)).name
            actual = HomeOrAway(int(actuals[i])).name
            results_table.append([teams, prediction, actual])
            
        Utility.print_table(results_table)
    
    @staticmethod
    def get_games_for_date_range(client, date_range):
        pass
        
    @staticmethod
    def get_games_for_date(client, date):
        date = parser.parse(date)
        schedule = client.schedule.daily_schedule(str(date)[:10])
        return schedule["games"], schedule["numberOfGames"]