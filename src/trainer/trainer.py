from typing import List

from shared.logging_config import LoggingConfig
from model.algorithms import Algorithms
from trainer.linear_regression import TrainLinearRegression

logger = LoggingConfig.get_logger(__name__)

class Trainer:

    @staticmethod
    def train(
        algorithm: Algorithms,
        output: str,
        data_files: List[str]
    ):
        match algorithm:
            case Algorithms.linear_regression:
                TrainLinearRegression.train(output, data_files)
            case _:
                logger.error("Invalid algorithm provided to predict.")