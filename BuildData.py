import json
import logging

from nhlpy import NHLClient

from model.GameEntry import GameEntry
from model.GameType import GameType
from model.Seasons import PastSeasons
from model.TeamMap import TeamMap

logger = logging.getLogger(__name__)
logging.basicConfig(filename="buildData.log", level=logging.INFO)
logger.info("Starting data fetch")

"""
Avoid multiple rows for a single game by recoding the IDs for games already processed.
"""
games_processed = []

"""
Cache the generated rows to write out to csv
"""
data = []

client = NHLClient()

bail_out = False # TODO: remove me

for season in PastSeasons:
    logger.info(f"Start of processing for season '{season}'.")
    
    for team in TeamMap:
        try:
            logger.info(f"Start processing for team '{team}' in season '{season}'.")
            
            games = client.schedule.team_season_schedule(team, season)["games"]
            logger.info(f"Found '{len(games)}' games for team '{team}' in season '{season}'.")
            
            for game in games:
                try:
                    if game["id"] in games_processed:
                        logger.info(f"Skipping game '{game["id"]}' which was already processed.")
                        continue
                    games_processed.append(game["id"])
                    box_score = client.game_center.boxscore(game["id"])
                    if box_score["gameType"] != GameType.RegularSeason.value:
                        logger.info(f"Skipping game '{game["id"]}' which is not a regular season game.")
                        continue
                    entry = repr(GameEntry.from_json(box_score))
                    logger.info(f"Adding game entry to data set: '{entry}'.")
                    data.append(entry)
                    
                    # TODO: remove this...
                    print(json.dumps(games, indent=4))
                    print(json.dumps(box_score, indent=4))
                    bail_out = True
                    break


                except Exception as e:
                    logger.exception(f"Exception processing box_score query: '{str(e)}'.", stack_info=True)

                # TODO: Remove This.
                if bail_out:
                    break
        
        except Exception as e:
            logger.exception(f"Exception processing team_season_schedule query: '{str(e)}'.", stack_info=True)
        # TODO: Remove this
        if bail_out:
            break
        
    # TODO: Remove this
    if bail_out:
        break

#print(data) # TODO: remove debugging statement
print(f"Total games added to database: '{len(games_processed)}'.") # TODO: Remove debugging statement

logger.info("Completed data fetch")