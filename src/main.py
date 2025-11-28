from typing import List, Optional

import typer
from typing_extensions import Annotated

from databuilder.data_builder import DataBuilder
from model.algorithms import Algorithms
from predictor.predictor import Predictor
from trainer.trainer import Trainer

app = typer.Typer()

@app.command()
def build(
):
    """
    Build the data set.
    """
    DataBuilder.build()

@app.command()
def train(
    algorithm: Annotated[Algorithms, typer.Option(
        help="Specify which ML algorithm to use.",
        case_sensitive=False,
        prompt=True
    )],
    output: Annotated[str, typer.Option(
        help="Specify the file name for the serialized model."
    )],
    data_file: Annotated[Optional[List[str]], typer.Option(
        help="Specify one or more data files which make up the data set to train on."
    )],
):
    """
    Train a model
    """
    Trainer.train(algorithm, output, data_file)

@app.command()
def predict(
    algorithm: Annotated[Algorithms, typer.Option(
        help="Specify which ML algorithm to use.",
        case_sensitive=False,
        prompt=True
    )],
    model: Annotated[str, typer.Option(
        help="Specify a pickle file containing the pre-trained model to use.",
        prompt=True
    )],
    date: Annotated[str, typer.Option(
        help=(
            "Specify a date, all games for this date will be retrieved. This "
            "option superscedes the 'date_range' option."
        )
    )] = None,
    date_range: Annotated[str, typer.Option(
        help=(
            "Specify a range of dates, all games occuring during this range "
            "will be retrieved.  if a date is supplied, this option will be "
            "ignored."
            "\n\n THIS IS NOT IMPLEMENTED YET."
            #TODO: Remove the not implemented disclaimer when appropriate
        )
    )] = None,
    summarizer: Annotated[str, typer.Option(
        help="Specify the algorithm to use to summarize roster strength."
    )] = None
):
    """
    Predict the outcome of a game(s) given the specified model.
    """
    Predictor.predict(algorithm, model, summarizer, date, date_range)

if __name__ == "__main__":
    app()