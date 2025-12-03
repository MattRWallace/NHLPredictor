from enum import Enum

"""
Seasons to use when fetching data from the API.  This is the data that we will
be training and testing our model with.

Since I only care about predicting Kraken performance so I only go back to their
first year.  I might increase the scope in the future for better accuracy, but
for now I value the smaller dataset for performance reasons.
"""
class PastSeasons(str, Enum):
    _20222023 = "20222023"
    _20232024 = "20232024"
    _20242025 = "20242025"

    @classmethod
    def items(cls):
        return [e for e in cls]

CurrentSeason = "20252026"