from model.team_map import TeamMap

"""
Represents a single game entry in the dataset.
"""
class GameEntry:
    def __init__(
            self, 
            num_periods, 
            winner_score, 
            winner_sog,
            loser_score,
            loser_sog,
            winning_franchise):
        self._num_periods = num_periods
        self._winner_score = winner_score
        self._winner_sog = winner_sog
        self._loser_score = loser_score
        self._loser_sog = loser_sog
        self._winning_franchise = winning_franchise

    """
    Takes a JSON data object and initializes a new GameEntry
    from it.
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
            winner_score = homeTeamScore
            winner_sog = homeTeamSog
            loser_score = awayTeamScore
            loser_sog = awayTeamSog
        else:
            winner_score = awayTeamScore
            winner_sog = awayTeamSog
            loser_score = homeTeamScore
            loser_sog = homeTeamSog

        winning_franchise = (
            TeamMap[homeTeamAbbrev]
            if homeTeamScore > awayTeamScore
            else TeamMap[awayTeamAbbrev]
            )

        obj =  cls(
            json_data["periodDescriptor"]["number"], 
            winner_score,
            winner_sog,
            loser_score,
            loser_sog,
            winning_franchise
            )
        return obj


    """
    serialize the game data into a row for the CSV file
    """
    def __repr__(self):
        return (
            f"{self._num_periods},{self._winner_score},"
            f"{self._winner_sog},{self._loser_score},"
            f"{self._loser_sog},{self._winning_franchise}"
            )
