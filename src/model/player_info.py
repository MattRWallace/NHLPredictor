import pandas as pd

"""
Class to represent a single player's stats set.
"""
    
class PlayerInfo:
    
    def __init__(
            self,
            goals,
            assists,
            points,
            plus_minus,
            pim,
            hits,
            pp_goals,
            sog,
            faceoff_win_pct,
            toi,
            blocked_shots,
            giveaways,
            takeaways
            ):
        self.goals = goals
        self.assists = assists
        self.points = points
        self.plus_minus = plus_minus
        self.pim = pim
        self.hits = hits
        self.pp_goals = pp_goals
        self.sog = sog
        self.faceoff_win_pct = faceoff_win_pct
        self.toi = toi
        self.blocked_shots = blocked_shots
        self.giveaways = giveaways
        self.takeaways = takeaways
    
    @classmethod
    def from_json(cls, json_data):
        # TODO: Need to gracefully handle missing data
        
        # TODO: Is there a neater way to do this?
        toi = json_data["toi"]
        if str(toi).count(":") == 1:
            toi = f"00:{toi}"
        toi = pd.to_timedelta(toi).total_seconds()
        
        obj = cls(
            json_data["goals"],
            json_data["assists"],
            json_data["points"],
            json_data["plusMinus"],
            json_data["pim"],
            json_data["hits"],
            json_data["powerPlayGoals"],
            json_data["sog"],
            json_data["faceoffWinningPctg"],
            toi,
            json_data["blockedShots"],
            json_data["giveaways"],
            json_data["takeaways"]
        )
        
        return obj
    
    """
    serialize the game data into a row for the CSV file
    """
    def __repr__(self):
        return (
            f"{self.goals},{self.assists},"
            f"{self.points},{self.plus_minus},"
            f"{self.pim},{self.hits}"
            f"{self.pp_goals},{self.sog}"
            f"{self.faceoff_win_pct},{self.toi}"
            f"{self.blocked_shots},{self.giveaways}"
            f"{self.takeaways}"
            )