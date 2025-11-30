from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from builder.builder import Builder
from model.algorithms import Algorithms
from model.seasons import PastSeasons
from model.summarizers import Summarizers
from predictor.predictor import Predictor
from shared.execution_context import ExecutionContext
from trainer.trainer import Trainer

app = typer.Typer()

_summarizer = Annotated[Summarizers, typer.Option(
        help="Specify the algorithm to use to summarize roster strength."
    )]

_algorithm = Annotated[Algorithms, typer.Option(
        help="Specify which ML algorithm to use.",
        case_sensitive=False,
        prompt=True
    )]

_app_root = Annotated[Path, typer.Option(
    help=(
        "Specify the location to save related files. Default location is "
        "'~/.config/nhlpredictor'"
    )
)]

_update = Annotated[bool, typer.Option(
    help="Allow overwriting of existing files. By default, the app will not overwite."
)]

@app.command()
def build(
    season: Annotated[Optional[List[PastSeasons]], typer.Option(
        help=(
            "Specify the seasons to include. If '--all-seasons' is specified, "
            "this option will be ignored."
        )
    )] = None,
    summarizer: _summarizer = None,
    all_seasons: Annotated[bool, typer.Option(
        help=(
            "Indicates that all seasons should be included in the data set. "
            "This option superscedes the '--season' option. See '--season' hints "
            "for list of seasons included."
        )
    )] = False,
    update: _update = False
):
    """
    Build the data set.
    """
    ExecutionContext.allow_update = update
    Builder.build(season, summarizer, all_seasons)

@app.command()
def train(
    algorithm: _algorithm,
    data_file: Annotated[Optional[List[str]], typer.Option(
        help="Specify one or more data files which make up the data set to train on."
    )],
    output: Annotated[str, typer.Option(
        help="Specify the file name for the serialized model."
    )],
    update: _update = False
):
    """
    Train a model using the specified ML algorithm and data.
    """
    Trainer.train(algorithm, output, data_file)

@app.command()
def predict(
    algorithm: _algorithm,
    model: Annotated[str, typer.Option(
        help="Specify a pickle file containing the pre-trained model to use.",
        prompt=True
    )],
    date: Annotated[str, typer.Option(
        help=(
            "Specify a date, all games for this date will be retrieved. This "
            "option superscedes the '--date-range' option."
        )
    )] = None,
    date_range: Annotated[str, typer.Option(
        help=(
            "Specify a range of dates, all games occuring during this range "
            "will be retrieved.  If '--date' is specified, this option will be "
            "ignored."
            "\n\nParsing of date range is performed by daterangeparser. See "
            "documentation for supported formats: "
            "https://daterangeparser.readthedocs.io/en/latest/\n"
            "\033[91m THIS IS NOT IMPLEMENTED YET.\033[91m"
            #TODO: Remove the not implemented disclaimer when appropriate
        )
    )] = None,
    summarizer: _summarizer = None,
    use_season_totals: Annotated[bool, typer.Option(
        help=(
            "Specify to use only the current season stats for prediction. By default the "
            "player's career stats are used.  Once the season has progressed enough, you "
            "may get more accuate results using current season stats."
        )
    )] = False
):
    """
    Predict the outcome of a game(s) given the specified model.
    """
    Predictor.predict(algorithm, model, summarizer, date, date_range)

if __name__ == "__main__":
    app()