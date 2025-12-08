from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from model.algorithms import Algorithms
from model.seasons import Seasons
from model.summarizers import Summarizers
from shared.execution_context import ExecutionContext

app = typer.Typer()

_summarizer = Annotated[Summarizers, typer.Option(
        help="Specify the algorithm to use to summarize roster strength.",
        prompt=True
    )]

_algorithm = Annotated[Algorithms, typer.Option(
        help="Specify which ML algorithm to use.",
        case_sensitive=False,
        prompt=True
    )]

_app_dir = Annotated[Path, typer.Option(
    help=(
        "Specify the location to save related files. Default location is "
        "'~/.config/nhlpredictor'"
    )
)]

@app.command()
def build(
    season: Annotated[Optional[List[Seasons]], typer.Option(
        help=(
            "Specify the seasons to include. If '--all-seasons' is specified, "
            "this option will be ignored."
        )
    )] = None,
    all_seasons: Annotated[bool, typer.Option(
        help=(
            "Indicates that all seasons should be included in the data set. "
            "This option superscedes the '--season' option. See '--season' hints "
            "for list of seasons included."
        )
    )] = False,
    update: Annotated[bool, typer.Option(
        help=(
            "Existing tables will be cleared and repopulated."
        )
    )] = False,
    report: Annotated[bool, typer.Option(
        help=(
            "Reports on the current status of the database.  No alteration of "
            "of data will occur."
        )
    )] = False,
    app_dir: _app_dir = None
):
    """
    Build the data set.
    """
    context = ExecutionContext()
    context.allow_update = update
    if app_dir:
        context.app_dir = app_dir

    from builder.builder import Builder
    if report:
        Builder.report()
    else:
        Builder.build(season, all_seasons)

@app.command()
def train(
    algorithm: _algorithm,
    output: Annotated[str, typer.Option(
        help="Specify the file name for the serialized model."
    )],
    update: Annotated[bool, typer.Option(
        help=(
            "Allow serialized model to be overwritten."
        )
    )] = False,
    app_dir: _app_dir = None
):
    """
    Train a model using the specified ML algorithm and data.
    """
    context = ExecutionContext()
    if app_dir:
        context.app_dir = app_dir
    context.output_file = output
    context.allow_update = update
    
    from trainer.trainer import Trainer
    Trainer.train(algorithm)

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
    )] = False,
    app_dir: _app_dir = None
):
    """
    Predict the outcome of a game(s) given the specified model.
    """
    context = ExecutionContext()
    if app_dir:
        context.app_dir = app_dir
    
    from predictor.predictor import Predictor
    Predictor.predict(algorithm, model, summarizer, date, date_range)

if __name__ == "__main__":
    app()