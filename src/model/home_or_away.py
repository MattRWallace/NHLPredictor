from enum import Enum

"""
Designate a team as Home or Away
"""
class HomeOrAway(Enum):
    NONE, HOME, AWAY = range(3)