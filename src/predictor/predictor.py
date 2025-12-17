from daterangeparser import parse as drp
from nhlpy.nhl_client import NHLClient

from model.algorithms import Algorithms
from model.summarizers.average_player_summarizer import AveragePlayerSummarizer
from model.summarizer_manager import Summarizers
from predictor.linear_regression import PredictLinearRegression
from shared.logging_config import LoggingConfig

logger = LoggingConfig.get_logger(__name__)

class Predictor:
    
    @staticmethod
    def predict(
        algorithm: Algorithms,
        model_file_name: str,
        summarizer_type: str = None,
        date: str = None,
        date_range: str = None,
        use_season_totals: bool = False
    ):
        summarizer = Summarizers.get_summarizer(summarizer_type)
        date_range_start = date_range_end = None
        if date_range is not None:
            date_range_start, date_range_end = drp(date_range)

        match algorithm:
            case Algorithms.linear_regression:
                PredictLinearRegression.predict(
                    summarizer,
                    model_file_name,
                    date,
                    date_range_start,
                    date_range_end,
                    use_season_totals
                    )
            case _:
                logger.error("Invalid algorithm provided to predict.")
