
from enum import Enum

"""
Enum mapping game type labels to the numerical value used by the
NHL API to indicate game type.

Since the NHL doesn't document their API, value map was obtained
from here:
https://github.com/Zmalski/NHL-API-Reference/issues/23#issuecomment-2492925102
"""
class GameState(str, Enum):
    Future = "FUT"
    Pregame = "PRE"
    Live = "LIVE"
    Final = "FINAL"
    Official = "OFF"