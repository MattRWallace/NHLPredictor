from datetime import timedelta
from pickle import load

import dateutil.parser as parser
import numpy as np
import pandas as pd

from builder.builder import Builder
from model.home_or_away import HomeOrAway
from shared.execution_context import ExecutionContext
from shared.logging_config import LoggingConfig
from shared.utility import Utility

logger = LoggingConfig.get_logger(__name__)
execution_context = ExecutionContext()

class PredictLinearRegression:

    @staticmethod
    def predict(
        summarizer,
        model_file_name,
        date,
        date_range_start,
        date_range_end,
        use_season_totals
    ):
        data = []
        results_table = [["Game", "Predicted", "Actual"]]
        with open(model_file_name, "rb") as file:
            model = load(file)

        if date is not None:
            date = parser.parse(date)
            games, number_of_games = (
                PredictLinearRegression.get_games_for_date(date)
            )
        elif date_range_start is not None and date_range_end is not None:
            games, number_of_games = (
                PredictLinearRegression.get_games_for_date_range(date_range_start, date_range_end)
            )
        else:
            logger.error("No valid date option supplied")
            return

        if (number_of_games <= 0):
            logger.warning("No games on the schedule for chosen date(s).")
            return

        # TODO: No referencing back to the builder
        # for game in games:
        #     logger.info(f"Processing game. ID: '{game["id"]}'.")
        #     box_score = execution_context.client.game_center.boxscore(game["id"])
        #     entry = Builder.process_game_historical(box_score, summarizer, use_season_totals)
        #     if entry is not None:
        #         data.append(entry)

        if (len(data)) == 0:
            logger.warning("None of the specified games have released rosters yet.")
            # TODO: Probably need something here for usability.  Maybe print out
            # a message, an empty results table or even update logging to send
            # warnings to the console?
            print("None of the specified games have released rosters yet.")
            return

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
    def get_games_for_date_range(date_range_start, date_range_end):
        games = []
        number_of_games = 0

        number_of_days = (date_range_end - date_range_start).days + 1
        date_list = [date_range_end - timedelta(days=x) for x in range(number_of_days)]
        for date in date_list:
            next_games, next_number = PredictLinearRegression.get_games_for_date(date)
            games.extend(next_games)
            number_of_games += next_number

        return games, number_of_games

    @staticmethod
    def get_games_for_date(date):
        schedule = execution_context.client.schedule.daily_schedule(str(date)[:10])
        return schedule["games"], schedule["numberOfGames"]