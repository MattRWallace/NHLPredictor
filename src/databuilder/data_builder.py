import json
import logging

import pandas as pd
from nhlpy import NHLClient

from model.game_entry import GameEntry
from model.game_type import GameType
from model.player_info import PlayerInfo
from model.seasons import PastSeasons
from model.team_map import TeamMap

logger = logging.getLogger("BuildData")
logging.basicConfig(filename="buildData.log", level=logging.INFO)
logger.info("Starting data fetch")


class DataBuilder:
    
    _client = NHLClient()

    @staticmethod
    def build_games():
        
        """
        Avoid multiple rows for a single game by recoding the IDs for games already processed.
        """
        games_processed = []

        for season in PastSeasons:
            data = []
            logger.info(f"Start of processing for season '{season}'.")
            
            for team in TeamMap:
                try:
                    logger.info(f"Start processing for team '{team}' in season '{season}'.")
                    
                    games = DataBuilder._client.schedule.team_season_schedule(team, season)["games"]
                    logger.info(f"Found '{len(games)}' games for team '{team}' in season '{season}'.")
                    
                    for game in games:
                        try:
                            if game["id"] in games_processed:
                                logger.info(f"Skipping game '{game["id"]}' which was already processed.")
                                continue
                            games_processed.append(game["id"])
                            box_score = DataBuilder._client.game_center.boxscore(game["id"])
                            if box_score["gameType"] != GameType.RegularSeason.value:
                                logger.info(f"Skipping game '{game["id"]}' which is not a regular season game.")
                                continue
                            
                            # Get roster scores
                            homeRoster = DataBuilder.build_players(
                                box_score["playerByGameStats"]["homeTeam"]
                                )
                            
                            awayRoster = DataBuilder.build_players(
                                box_score["playerByGameStats"]["awayTeam"]
                                )
                            
                            entry = GameEntry.from_json(box_score)
                            entry.add_roster(homeRoster, awayRoster)
                            
                            logger.info(f"Adding game entry to data set: '{entry}'.")
                            data.append(repr(entry).split(','))

                        except Exception as e:
                            print("\033[31mException occured. Check logs.\033[0m")
                            logger.exception(f"Exception processing box_score query. Exception: '{str(e)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(f"Exception processing team_season_schedule query. Exception: '{str(e)}', games: '{json.dumps(games, indent=4)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

            df = pd.DataFrame(data, columns=GameEntry.get_headers())
            df.to_csv(f"{season}.csv", index=False)
                                
        logger.info("Completed data fetch")

    @staticmethod
    def build_players(roster):
        forwards = DataBuilder.summarize_skaters(roster["forwards"])
        defense = DataBuilder.summarize_skaters(roster["defense"])
        # home_goalies = DataBuilder.summarize_goalie(homeRoster["goalies"])
        return f"{forwards},{defense}"
        
    @staticmethod
    def summarize_skaters(players):
        player_objects = []
        for player in players:
            player_objects.append(PlayerInfo.from_json(player))
        
        count = 0   
        goals = 0
        assists = 0
        points = 0
        plus_minus = 0
        pim = 0
        hits = 0
        pp_goals = 0
        sog = 0
        faceoff_win_pct = 0
        toi = 0
        blocked_shots = 0
        giveaways = 0
        takeaways = 0
        
        for player in player_objects:
            count += 1
            goals += player.goals
            assists += player.assists
            points += player.points
            plus_minus += player.plus_minus
            pim += player.pim
            hits += player.hits
            pp_goals += player.pp_goals
            sog += player.sog
            faceoff_win_pct += player.faceoff_win_pct
            toi += player.toi
            blocked_shots += player.blocked_shots
            giveaways += player.giveaways
            takeaways += player.takeaways

        
        # TODO: can't just average the FO %, it needs to be weighted    
        summary = PlayerInfo(
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
        )
        return repr(summary)
    
    @staticmethod
    def summarize_goalie(players):
        pass