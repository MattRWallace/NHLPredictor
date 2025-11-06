"""
Represents a single game entry in the dataset.
"""
class GameEntry:
    def __init__(
            self, 
            num_periods, 
            home_score, 
            home_sog,
            away_score,
            away_sog):
        self._num_periods = num_periods
        self._home_score = home_score
        self._home_sog = home_sog
        self._away_score = away_score
        self._away_sog = away_sog

    """
    Takes a JSON data object and initializes a new GameEntry
    from it.
    """
    @classmethod
    def from_json(cls, json_data):
        obj =  cls(
            json_data["periodDescriptor"]["number"], 
            json_data["homeTeam"]["score"],
            json_data["homeTeam"]["sog"],
            json_data["awayTeam"]["score"],
            json_data["awayTeam"]["sog"]
            )
        return obj


    """
    serialize the game data into a row for the CSV file
    """
    def __repr__(self):
        return f"{self._num_periods},{self._home_score},{self._home_sog},{self._away_score},{self._away_sog}"
