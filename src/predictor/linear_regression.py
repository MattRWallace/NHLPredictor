import os
from pickle import load
from typing import Dict

import numpy as np
import pandas as pd

from model.home_or_away import HomeOrAway
from model.summarizer_manager import SummarizerTypes
from shared.execution_context import ExecutionContext
from shared.logging_config import LoggingConfig
from shared.constants.json import JSON as Keys
from shared.utility import Utility as utl

logger = LoggingConfig.get_logger(__name__)
execution_context = ExecutionContext()
# summarizer = SummarizerTypes.get_summarizer(execution_context.summarizer_type)
_model_filename_part = "LinearRegression"

class PredictLinearRegression:

    @staticmethod
    def predict(
        games: Dict[str, object],
        number_of_games: int
    ):
        data = []
        results_table = [["Game", "Predicted", "Actual"]]
        summarizer = SummarizerTypes.get_summarizer(execution_context.summarizer_type)
        
        if execution_context.model:
            model_filename = execution_context.output_file
        else:
            model_filename = f"{summarizer.get_filename_prefix()}_{_model_filename_part}.pkl"
        with open(os.path.join(execution_context.app_dir, model_filename), "rb") as file:
            model = load(file)

        if (number_of_games <= 0):
            logger.warning("No games on the schedule for chosen date(s).")
            return

        # TODO: No referencing back to the builder
        for game in games:
            logger.info(f"Processing game. ID: '{utl.json_value_or_default(game, Keys.id)}'.")
            box_score = execution_context.client.game_center.boxscore(
                utl.json_value_or_default(game, Keys.id)
            )
            
            entry = Builder.process_game_historical(box_score, summarizer, use_season_totals)
            if entry is not None:
                data.append(entry)

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

        utl.print_table(results_table)