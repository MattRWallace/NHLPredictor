from enum import Enum

"""
Designate a team as Home or Away
"""
class HomeOrAway(Enum):
    AWAY = -1
    NONE = 0
    HOME = 1