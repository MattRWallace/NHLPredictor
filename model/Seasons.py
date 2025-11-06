"""
Seasons to fetch game data from.  This is the data that we will
be training and testing our model with.

Since I only care about predicting Kraken performance so I only
go back to their first year.  I might increase the scope in the
future for better accuracy, but for now I value the smaller
dataset for performance reasons.
"""
PastSeasons = [
    20222023,
    20232024,
    20242025
]

"""
The season that we're predicting results for
"""
CurrentSeason = 20252026