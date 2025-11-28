from nhlpy.nhl_client import NHLClient

from loggingconfig.logging_config import LoggingConfig
from model.algorithms import Algorithms
from model.average_player_summarizer import AveragePlayerSummarizer
from predictor.linear_regression import PredictLinearRegression

logger = LoggingConfig.get_logger(__name__)

class Predictor:
    
    @staticmethod
    def predict(
        algorithm: Algorithms,
        model_file_name: str,
        summarizer_type: str = None,
        date: str = None,
        date_range: str = None
    ):
        # TODO: Need to actually switch on summarizer type.
        if summarizer_type is None:
            summarizer = AveragePlayerSummarizer()
        else:
            summarizer = AveragePlayerSummarizer()

        client = NHLClient()

        match algorithm:
            case Algorithms.linear_regression:
                PredictLinearRegression.predict(
                    summarizer,
                    client,
                    model_file_name,
                    date,
                    date_range)
            case _:
                logger.error("Invalid algorithm provided to predict.")
