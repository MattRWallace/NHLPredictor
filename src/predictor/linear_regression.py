import numpy as np
import pandas as pd
import json
from nhlpy import NHLClient
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

from model.seasons import PastSeasons
from model.average_player_summarizer import AveragePlayerSummarizer
from loggingconfig.logging_config import LoggingConfig
from databuilder.data_builder import DataBuilder

from pickle import load

from datetime import datetime, UTC, timedelta

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
        
        print(data)
        
    @staticmethod
    def get_todays_games(client):
        client = NHLClient()
        # TODO: Remove the offset
        #today = datetime.now(UTC).strftime('%Y-%m-%d')
        today = (datetime.now(UTC) - timedelta(1)).strftime('%Y-%m-%d')
        return client.schedule.daily_schedule(today)
    
Predictor.predict()
