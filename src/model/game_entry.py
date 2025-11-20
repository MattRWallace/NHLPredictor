from model.home_or_away import HomeOrAway
from model.team_map import TeamMap

"""
Class to represent a single game entry in the dataset.
"""
class GameEntry:
    def __init__(
            self, 
            num_periods, 
            winner_score, 
            winner_sog,
            loser_score,
            loser_sog,
            winning_franchise,
            winner):
        self._num_periods = num_periods
        self._winner_score = winner_score
        self._winner_sog = winner_sog
        self._loser_score = loser_score
        self._loser_sog = loser_sog
        self._winning_franchise = winning_franchise
        self._winner = winner

    """
    Labels for the dataset columns represented as a list of strings.
    """
    @classmethod
    def get_headers(cls):
        return [
            "periods",
            "winnerScore",
            "winnerSOG",
            "loserScore",
            "loserSOG",
            "winnerForwardGoals",
            "winnerForwardAssists",
            "winnerForwardPoints",
            "winnerForwardPlusMinus",
            "winnerForwardPIM",
            "winnerForwardHits",
            "winnerForwardPPG",
            "winnerForwardSOG",
            "winnerForwardFaceoffPct",
            "winnerForwardTOI",
            "winnerForwardBlockedShots",
            "winnerForwardGivaways",
            "winnerForwardTakeaways",
            "winnerDefenseGoals",
            "winnerDefenseAssists",
            "winnerDefensePoints",
            "winnerDefensePlusMinus",
            "winnerDefensePIM",
            "winnerDefenseHits",
            "winnerDefensePPG",
            "winnerDefenseSOG",
            "winnerDefenseFaceoffPct",
            "winnerDefenseTOI",
            "winnerDefenseBlockedShots",
            "winnerDefenseGivaways",
            "winnerDefenseTakeaways",
            "loserForwardGoals",
            "loserForwardAssists",
            "loserForwardPoints",
            "loserForwardPlusMinus",
            "loserForwardPIM",
            "loserForwardHits",
            "loserForwardPPG",
            "loserForwardSOG",
            "loserForwardFaceoffPct",
            "loserForwardTOI",
            "loserForwardBlockedShots",
            "loserForwardGivaways",
            "loserForwardTakeaways",
            "loserDefenseGoals",
            "loserDefenseAssists",
            "loserDefensePoints",
            "loserDefensePlusMinus",
            "loserDefensePIM",
            "loserDefenseHits",
            "loserDefensePPG",
            "loserDefenseSOG",
            "loserDefenseFaceoffPct",
            "loserDefenseTOI",
            "loserDefenseBlockedShots",
            "loserDefenseGivaways",
            "loserDefenseTakeaways",
            "winnerFranchiseId"
        ]

    """
    Takes a JSON data object and initializes a new GameEntry
    from it.

    Note: This only initializes the broad game information from the box score.
    player information for each game needs to be preprocessed before it can be
    added to the GameEntry.  See add_roster.
    """
    @classmethod
    def from_json(cls, json_data):
        homeTeamAbbrev = json_data["homeTeam"]["abbrev"]
        homeTeamScore = json_data["homeTeam"]["score"]
        homeTeamSog = json_data["homeTeam"]["sog"]
        awayTeamAbbrev = json_data["awayTeam"]["abbrev"]
        awayTeamScore = json_data["awayTeam"]["score"]
        awayTeamSog = json_data["awayTeam"]["sog"]

        if homeTeamScore > awayTeamScore:
            winner = HomeOrAway.HOME
            winning_franchise = TeamMap[homeTeamAbbrev]
        else:
            winner = HomeOrAway.AWAY
            winning_franchise = TeamMap[awayTeamAbbrev]

        if winner == HomeOrAway.HOME:
            winner_score = homeTeamScore
            winner_sog = homeTeamSog
            loser_score = awayTeamScore
            loser_sog = awayTeamSog
        else:
            winner_score = awayTeamScore
            winner_sog = awayTeamSog
            loser_score = homeTeamScore
            loser_sog = homeTeamSog

        obj =  cls(
            json_data["periodDescriptor"]["number"], 
            winner_score,
            winner_sog,
            loser_score,
            loser_sog,
            winning_franchise,
            winner
            )
        return obj

    def add_roster(self, home_roster, away_roster):
        if self._winner == HomeOrAway.HOME:
            self._winning_roster = home_roster
            self._losing_roster = away_roster
        else:
            self._winning_roster = away_roster
            self._losing_roster = home_roster

    """
    serialize the game data into a row for the CSV file
    """
    def __repr__(self):
        return (
            f"{self._num_periods},{self._winner_score},"
            f"{self._winner_sog},{self._loser_score},"
            f"{self._loser_sog},{self._winning_roster},"
            f"{self._losing_roster},{self._winning_franchise}"
            )
