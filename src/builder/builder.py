import json

import pandas as pd
from nhlpy import NHLClient

from shared.execution_context import ExecutionContext
from shared.logging_config import LoggingConfig
from model.average_player_summarizer import AveragePlayerSummarizer
from model.game_entry import GameEntry
from model.game_type import GameType
from model.seasons import CurrentSeason, PastSeasons
from model.summarizers import Summarizers
from model.team_map import TeamMap

logger = LoggingConfig.get_logger(__name__)

class Builder:
    
    @staticmethod
    def build(
        seasons,
        summarizer_type,
        all_seasons: bool = False
    ):
        summarizer = Summarizers.get_summarizer(summarizer_type)

        if all_seasons:
            Builder.build_past_seasons(summarizer)
            Builder.build_current_season(summarizer)
        elif seasons is not None:
            Builder.build_seasons(seasons, summarizer)
        else:
            logger.error("Invalid season specification, cannot build data set.")

        Builder.build_seasons(seasons, summarizer)
        logger.info("Call to build_games is complete.")

    @staticmethod
    def build_seasons(
        seasons: PastSeasons,
        summarizer
    ):
        logger.info("Start building seasons.")
        
        # Avoid multiple rows for a single game by recoding the IDs for games already processed.
        games_processed = []

        for season in seasons:
            logger.info(f"Start of processing for season '{season.value}'.")

            # TODO: If not update and file exists, then continue
            
            data = []
            for team in TeamMap:
                try:
                    logger.info(f"Start processing for team '{team}' in season '{season.value}'.")
                    
                    games = ExecutionContext.client.schedule.team_season_schedule(team, season.value)["games"]
                    logger.info(f"Found '{len(games)}' games for team '{team}' in season '{season.value}'.")
                    
                    Builder.process_team(games, games_processed, data, summarizer)
                    
                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(
                        f"Exception processing team_season_schedule query. "
                        f"Games: '{json.dumps(games, indent=4)}',"
                        f"Exception: '{str(e)}'.",
                        stack_info=True)
                
            logger.info("Building DataFrame from game entries.")
            df = pd.DataFrame(data, columns=summarizer.get_headers())
            df.to_csv(f"{season.value}.csv", index=False)
            logger.info(f"DataFrame written to CSV. File: '{season.value}.csv'.")
                                
        logger.info("Completed building previous seasons.")

    @staticmethod
    def build_past_seasons(summarizer):
        logger.info("Start building past seasons.")
        Builder.build_seasons(PastSeasons.items(), summarizer)
        logger.info("Completed building previous seasons.")
    
    @staticmethod
    def build_current_season(summarizer):
        # TODO: We should short-circuit and skip trying to prcess future games already in the system.
        # Avoid multiple rows for a single game by recoding the IDs for games already processed.
        games_processed = []
        data = []
        
        for team in TeamMap:
            try:
                logger.info(f"Start processing for team '{team}' in season '{CurrentSeason}'.")
                
                games = ExecutionContext.client.schedule.team_season_schedule(team, CurrentSeason)["games"]
                logger.info(f"Found '{len(games)}' games for team '{team}' in season '{CurrentSeason}'.")
                
                Builder.process_team(games, games_processed, data, summarizer)
                
            except Exception as e:
                print("\033[31mException occured. Check logs.\033[0m")
                logger.exception(
                    f"Exception processing team_season_schedule query. "
                    f"Games: '{json.dumps(games, indent=4)}', "
                    f"Exception: '{str(e)}'.",
                    stack_info=True)
            
        logger.info("Building DataFrame from game entries.")
        df = pd.DataFrame(data, columns=summarizer.get_headers())
        df.to_csv("currentSeason.csv", index=False)
        logger.info("DataFrame written to CSV. File: 'currentSeason.csv'.")
        logger.info("Current season data build complete.")
    
    @staticmethod
    def process_team(games, games_processed, data, summarizer):
        try:
            for game in games:
                try:
                    if game["id"] in games_processed:
                        logger.info(f"Skipping game '{game["id"]}' which was already processed.")
                        continue
                    games_processed.append(game["id"])
                    box_score = ExecutionContext.client.game_center.boxscore(game["id"])
                    if box_score["gameType"] != GameType.RegularSeason.value:
                        logger.info(f"Skipping game '{game["id"]}' which is not a regular season game.")
                        continue
                    
                    data.append(Builder.process_game(box_score, summarizer))

                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(f"Exception processing box_score query. Exception: '{str(e)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

        except Exception as e:
            print("\033[31mException occured. Check logs.\033[0m")
            logger.exception(f"Exception processing team_season_schedule query. Exception: '{str(e)}', games: '{json.dumps(games, indent=4)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

    @staticmethod
    def process_game(box_score, summarizer ):
        logger.info("Summarizing rosters.")
        if "playerByGameStats" not in box_score:
            logger.warning("Roster not published yet")
            return None
        summary = summarizer.summarize(
            box_score["playerByGameStats"]["homeTeam"],
            box_score["playerByGameStats"]["awayTeam"]
        )
        logger.info("Rosters summarized.")
        
        entry = GameEntry.from_json(box_score)
        entry.add_roster(*summary)
        
        logger.info(f"Adding game entry to data set: '{entry}'.")
        return repr(entry).split(',')

    @staticmethod
    def process_game_historical(box_score, summarizer, use_season_totals):
        logger.info("Summarizing rosters with historical data.")
        if "playerByGameStats" not in box_score:
            logger.warning("Roster not published yet")
            return None

        summary = summarizer.summarize_historical(
            box_score["playerByGameStats"]["homeTeam"],
            box_score["playerByGameStats"]["awayTeam"],
            use_season_totals
        )
        logger.info("Rosters summarized.")

        entry = GameEntry.from_json(box_score)
        entry.add_roster(*summary)

        logger.info(f"Adding game entry to data set: '{entry}'.")
        return repr(entry).split(',')