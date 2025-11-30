from shared.logging_config import LoggingConfig
from model.home_or_away import HomeOrAway
from model.team_map import TeamMap

logger = LoggingConfig.get_logger(__name__)

"""
Class to represent a single game entry in the dataset.
"""
class GameEntry:
    def __init__(
            self, 
            num_periods, 
            home_score, 
            home_sog,
            away_score,
            away_sog,
            winner_home_or_away):
        self._num_periods = num_periods
        self._home_score = home_score
        self._home_sog = home_sog
        self._away_score = away_score
        self._away_sog = away_sog
        self._winner_home_or_away = winner_home_or_away

        logger.info("GameEntry created..")

    """
    Takes a JSON data object and initializes a new GameEntry
    from it.

    Note: This only initializes the broad game information from the box score.
    player information for each game needs to be preprocessed before it can be
    added to the GameEntry.  See add_roster.
    """
    @classmethod
    def from_json(cls, json_data):
        logger.info(f"Creating GameEntry from JSON data. JSON:'{json_data}'.")

        homeTeamScore = json_data["homeTeam"]["score"]
        homeTeamSog = json_data["homeTeam"]["sog"]
        awayTeamScore = json_data["awayTeam"]["score"]
        awayTeamSog = json_data["awayTeam"]["sog"]

        if homeTeamScore > awayTeamScore:
            winner_home_or_away = HomeOrAway.HOME
        else:
            winner_home_or_away = HomeOrAway.AWAY

        obj =  cls(
            json_data["periodDescriptor"]["number"], 
            homeTeamScore,
            homeTeamSog,
            awayTeamScore,
            awayTeamSog,
            winner_home_or_away.value
            )
        logger.info("Created GameEntry from JSON data.")

        return obj

    def add_roster(self, home_roster, away_roster):
        logger.info(f"Adding roster information to GameEntry. Home: '{home_roster}', Away: '{away_roster}'." )
        if self._winner_home_or_away == HomeOrAway.HOME:
            self._winning_roster = home_roster
            self._losing_roster = away_roster
        else:
            self._winning_roster = away_roster
            self._losing_roster = home_roster

    """
    serialize the game data into a row for the CSV file
    
    TODO: using repr and returning a string instead of a collection is a remnant of a 
    previous design.  Refactor/redesign this.
    """
    def __repr__(self):
        return (
            f"{self._num_periods},{self._home_score},"
            f"{self._home_sog},{self._away_score},"
            f"{self._away_sog},{self._winning_roster},"
            f"{self._losing_roster},{self._winner_home_or_away}"
            )
