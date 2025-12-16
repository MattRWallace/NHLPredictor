from model.algorithms import Algorithms
from shared.logging_config import LoggingConfig
from trainer.linear_regression import TrainLinearRegression

logger = LoggingConfig.get_logger(__name__)

class Trainer:

    @staticmethod
    def train(algorithm: Algorithms):
        match algorithm:
            case Algorithms.linear_regression:
                TrainLinearRegression.train()
            case _:
                logger.error("Invalid algorithm provided to predict.")