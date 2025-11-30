from datetime import timedelta

from shared.logging_config import LoggingConfig
from shared.utility import Utility

logger = LoggingConfig.get_logger(__name__)

"""
Super class for representing a single player's stats set.
"""
class PlayerInfo:
    def __init__(
            self,
            pim,
            toi):
        self.pim = pim
        self.toi = toi
        logger.info("Inititializing PlayerInfo.")

    @staticmethod
    def parse_toi(json_data):
        toi = Utility.json_value_or_default(json_data, "toi")
        # TODO: additional validation here? Could API provide a non-zero value without minutes?
        if toi == 0:
            return 0
        parsed = timedelta(hours=int(toi[:-3]), minutes=int(toi[-2:])).total_seconds()
        logger.info(f"Parsed TOI for PlayerInfo. TOI: '{parsed}'.")

        return parsed

"""
Class to represent a single skater's stats set.
"""
class SkaterInfo(PlayerInfo):
    
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
        super().__init__(pim, toi)
        self.goals = goals
        self.assists = assists
        self.points = points
        self.plus_minus = plus_minus
        self.hits = hits
        self.pp_goals = pp_goals
        self.sog = sog
        self.faceoff_win_pct = faceoff_win_pct
        self.blocked_shots = blocked_shots
        self.giveaways = giveaways
        self.takeaways = takeaways
        logger.info("Initialized SkaterInfo.")

    """
    Initialize a SkaterInfo object from JSON data
    """   
    @classmethod
    def from_json(cls, json_data):
        # TODO: Need to gracefully handle missing data

        obj = cls(
            Utility.json_value_or_default(json_data, "goals"),
            Utility.json_value_or_default(json_data, "assists"),
            Utility.json_value_or_default(json_data, "points"),
            Utility.json_value_or_default(json_data, "plusMinus"),
            Utility.json_value_or_default(json_data, "pim"),
            Utility.json_value_or_default(json_data, "hits"),
            Utility.json_value_or_default(json_data, "powerPlayGoals"),
            Utility.json_value_or_default(json_data, "sog"),
            Utility.json_value_or_default(json_data, "faceoffWinningPctg"),
            cls.parse_toi(json_data),
            Utility.json_value_or_default(json_data, "blockedShots"),
            Utility.json_value_or_default(json_data, "giveaways"),
            Utility.json_value_or_default(json_data, "takeaways")
        )
        logger.info(f"Created SkaterInfo from JSON. SkaterInfo: '{obj}'.")
        
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
    

"""
Class to represent a single goalie's stats set.
"""
class GoalieInfo(PlayerInfo):

    def __init__(
            self,
            es_shots_against,
            es_saves,
            pp_shots_against,
            pp_saves,
            sh_shots_against,
            sh_saves,
            save_shots_against,
            save_pct,
            es_goals_against,
            pp_goals_against,
            sh_goals_against,
            pim,
            goals_against,
            toi,
            # starter,
            # decision,
            shots_against,
            saves
            ):
        super().__init__(pim, toi)
        self.es_shots_against = es_shots_against
        self.es_saves = es_saves
        self.pp_shots_against = pp_shots_against
        self.pp_saves = pp_saves
        self.sh_shots_against = sh_shots_against
        self.sh_saves = sh_saves
        self.save_shots_against = save_shots_against
        self.save_pct = save_pct
        self.es_goals_against = es_goals_against
        self.pp_goals_against = pp_goals_against
        self.sh_goals_against = sh_goals_against
        self.goals_against = goals_against
        # self.starter = starter
        # self.decision = decision
        self.shots_against = shots_against
        self.saves = saves
        logger.info("Initialized GoalieInfo.")

    """
    Initialize a GoalieInfo object from JSON data
    """   
    @classmethod
    def from_json(cls, json_data):
        # TODO: Need to gracefully handle missing data
        obj = cls(
            *GoalieInfo.split_save_try_pair(
                Utility.json_value_or_default(json_data, "evenStrengthShotsAgainst")
            ),
            *GoalieInfo.split_save_try_pair(
                Utility.json_value_or_default(json_data, "powerPlayShotsAgainst")
            ),
            *GoalieInfo.split_save_try_pair(
                Utility.json_value_or_default(json_data, "shorthandedShotsAgainst")
            ),
            GoalieInfo.split_save_try_pair(
                Utility.json_value_or_default(json_data, "saveShotsAgainst")
            )[1],
            Utility.json_value_or_default(json_data, "savePctg"),   #TODO: need to weight and average this
            Utility.json_value_or_default(json_data, "evenStrengthGoalsAgainst"),
            Utility.json_value_or_default(json_data, "powerPlayGoalsAgainst"),
            Utility.json_value_or_default(json_data, "shorthandedGoalsAgainst"),
            Utility.json_value_or_default(json_data, "pim"),
            Utility.json_value_or_default(json_data, "goalsAgainst"),
            cls.parse_toi(json_data),
            # Utility.json_value_or_default(json_data, "starter"),  # TODO: ?
            # Utility.json_value_or_default(json_data, "decision"),  # TODO: ?
            Utility.json_value_or_default(json_data, "shotsAgainst"),
            Utility.json_value_or_default(json_data, "saves")
        )
        logger.info("Created GoalieInfo from JSON..")
        
        return obj
    
    """
    Some goalies stats are represented as a save/try pair.  For example, see
    shots against stats that are shown like 21/27 where 21 is the number of
    saves and 27 is the total attempts.
    """
    @staticmethod
    def split_save_try_pair(value):
        parts = str(value).split('/')
        parts = [int(part) for part in parts]

        return tuple(parts)
    
    """
    serialize the player data as a csv string
    """
    def __repr__(self):
        return (
            f"{self.es_shots_against},{self.es_saves},"
            f"{self.pp_shots_against},{self.pp_saves},"
            f"{self.sh_shots_against},{self.sh_saves},"
            f"{self.save_shots_against},{self.save_pct},"
            f"{self.es_goals_against},{self.pp_goals_against},"
            f"{self.sh_goals_against},{self.pim},"
            f"{self.goals_against},{self.toi},"
            # f"{self.starter},{self.decision},"
            f"{self.shots_against},{self.saves}"
            )