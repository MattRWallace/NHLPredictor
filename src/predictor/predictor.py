from daterangeparser import parse as drp
from datetime import datetime, timedelta
import dateutil.parser as parser

from model.algorithms import Algorithms
from predictor.linear_regression import PredictLinearRegression
from shared.constants.json import JSON as Keys
from shared.execution_context import ExecutionContext
from shared.logging_config import LoggingConfig
from shared.utility import Utility as utl

logger = LoggingConfig.get_logger(__name__)
execution_context = ExecutionContext()

class Predictor:
    
    @staticmethod
    def predict(
        algorithm: Algorithms,
        date: str = None,
        date_range: str = None,
        use_season_totals: bool = False
    ) -> None:
        games, num_games = Predictor._get_games(date, date_range)
        match algorithm:
            case Algorithms.linear_regression:
                PredictLinearRegression.predict(
                    games,
                    num_games
                )
            case _:
                logger.error("Invalid algorithm provided to predict.")
    
    @staticmethod
    def predict_single_game(
        algorithm: Algorithms,
        game_id: str
    ):
        pass
    
    @staticmethod
    def list_games(
        date: str,
        date_range: str
    ):
        table = []
        games, num_games = Predictor._get_games(date, date_range)
        table.append([Keys.game_id, Keys.away_team, Keys.home_team, Keys.game_state])
        for game in games:
            table.append([
                str(utl.json_value_or_default(game, Keys.id)),
                str(utl.json_value_or_default(game, Keys.away_team, Keys.common_name, Keys.default)),
                str(utl.json_value_or_default(game, Keys.home_team, Keys.common_name, Keys.default)),
                str(utl.json_value_or_default(game, Keys.game_state))
            ])
        utl.print_table(table, hasHeader=True)

    @staticmethod
    def _parse_date_range(
        date_range: str
    ) -> tuple[datetime, ...]:
        date_range_start = date_range_end = None
        if date_range is not None:
            date_range_start, date_range_end = drp(date_range)
        return date_range_start, date_range_end
    
    @staticmethod
    def _get_games(
        date: str,
        date_range: str
    ):
        date_range_start, date_range_end = Predictor._parse_date_range(date_range)
        if date is not None:
            date = parser.parse(date)
            return Predictor._get_games_for_date(date)
        elif date_range_start is not None and date_range_end is not None:
            return Predictor._get_games_for_date_range(date_range_start, date_range_end)
        else:
            # TODO: Throw?
            logger.error("No valid date option supplied")
            return

    @staticmethod
    def _get_games_for_date_range(
        date_range_start,
        date_range_end
    ) -> tuple[object, int]:
        games = []
        number_of_games = 0
        number_of_days = (date_range_end - date_range_start).days + 1
        date_list = [date_range_end - timedelta(days=x) for x in range(number_of_days)]
        for date in date_list:
            next_games, next_number = Predictor._get_games_for_date(date)
            games.extend(next_games)
            number_of_games += next_number
        return games, number_of_games

    @staticmethod
    def _get_games_for_date(date) -> tuple[object, int]:
        schedule = execution_context.client.schedule.daily_schedule(str(date)[:10])
        return schedule["games"], schedule["numberOfGames"]