import json

from nhlpy import NHLClient

supported_seasons = [
    "20222023",
    "20232024",
    "20242025",
    "20252026"
]

"""
This is the set of team IDs for the current teams in the leage.
Note: Team id is a different identifier than franchise ID

TODO: This is a working list.  Depending on implementation, a map
of some sort might be better.  E.g. FranchiseId => TeamId
"""
current_teams = [
    55, # Kraken
]

client = NHLClient()

"""
teams = client.teams.teams()
kraken = [x for x in teams if x["abbr"] == "SEA"][0]
standings = client.standings.league_standings()
games = client.schedule.daily_schedule()
players = client.players.players_by_team("SEA", 20252026)

class PlayerStats:
    def __init__(self, value):
        self.__dict__.update(value)

stats = client.stats.skater_stats_summary(20252026, 20252026, franchise_id=39)
filtered_stats = [ PlayerStats(item) for item in stats]
print(json.dumps(stats, indent=4))
"""


teams = client.teams.teams()
print(json.dumps(teams[11], indent=4))

print(teams[11]["franchise_id"])

# Why does this return multiple season of data when only one season is specified?
teamStats = client.stats.team_summary(20242025, 20242025, default_cayenne_exp = "teamFullName='Seattle Kraken'")
print(json.dumps(teamStats, indent=4))