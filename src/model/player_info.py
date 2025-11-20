from datetime import timedelta

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

    """
    Initialize a PlayerInfo object from JSON data
    """   
    @classmethod
    def from_json(cls, json_data):
        # TODO: Need to gracefully handle missing data
        toi = json_data["toi"]
        toi = timedelta(hours=int(toi[:-3]), minutes=int(toi[-2:])).total_seconds()
        
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
    serialize the player data as a csv string
    """
    def __repr__(self):
        return (
            f"{self.goals},{self.assists},"
            f"{self.points},{self.plus_minus},"
            f"{self.pim},{self.hits},"
            f"{self.pp_goals},{self.sog},"
            f"{self.faceoff_win_pct},{self.toi},"
            f"{self.blocked_shots},{self.giveaways},"
            f"{self.takeaways}"
            )