import json

import pandas as pd
from sqlitedict import SqliteDict

from model.game_entry import GameEntry
from model.game_type import GameType, SupportedGameTypes
from model.seasons import CurrentSeason, PastSeasons
from model.team_map import TeamMap
from shared.constants.database import Database as DB
from shared.constants.json import JSON as Keys
from shared.execution_context import ExecutionContext
from shared.logging_config import LoggingConfig
from shared.utility import Utility as utl

logger = LoggingConfig.get_logger(__name__)
execution_context = ExecutionContext()
summarizer = execution_context.summarizer


class Builder:
    
    @staticmethod
    def build(
        seasons,
        all_seasons: bool = False
    ):
        if(execution_context.experimental):
            if all_seasons:
                Builder.build_past_seasons()
                Builder.build_current_season()
            elif seasons is not None:
                Builder.build_seasons_db(seasons)
            else:
                logger.error("Invalid season specification, cannot build data set.")
            return

        if all_seasons:
            Builder.build_past_seasons()
            Builder.build_current_season()
        elif seasons is not None:
            Builder.build_seasons(seasons)
        else:
            logger.error("Invalid season specification, cannot build data set.")

        Builder.build_seasons(seasons)
        logger.info("Call to build_games is complete.")

    @staticmethod
    def build_seasons_db(
        seasons: PastSeasons,
    ):
        logger.info("Start building seasons.")
        
        players_db = SqliteDict(
            utl.get_db_name(),
            tablename=DB.players_table_name,
            autocommit=True)
        skater_stats_db = SqliteDict(
            utl.get_db_name(),
            tablename=DB.skater_stats_table_name,
            autocommit=True
        )
        goalie_stats_db = SqliteDict(
            utl.get_db_name(),
            DB.goalie_stats_table_name,
            autocommit=True
        )
        games_db = SqliteDict(
            utl.get_db_name(),
            DB.games_table_name,
            autocommit=True
        )
        data = {
            DB.players_table_name: players_db,
            DB.skater_stats_table_name: skater_stats_db,
            DB.goalie_stats_table_name: goalie_stats_db,
            DB.games_table_name: games_db
        }
        
        for season in seasons:
            logger.info(f"Start of processing for season '{season.value}'.")

            # TODO: If not update and file exists, then continue
            
            for team in TeamMap:
                try:
                    logger.info(f"Start processing for team '{team}' in season '{season.value}'.")
                    
                    games_raw = execution_context.client.schedule.team_season_schedule(team, season.value)[Keys.games]
                    logger.info(f"Found '{len(games_raw)}' games for team '{team}' in season '{season.value}'.")

                    Builder.process_team_db(games_raw, data)
                    
                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(
                        f"Exception processing team_season_schedule query. "
                        f"Games: '{json.dumps(games_db, indent=4)}',"
                        f"Exception: '{str(e)}'.",
                        stack_info=True)
            
            
            logger.info("Building DataFrame from game entries.")
            # df = pd.DataFrame(data, columns=summarizer.get_headers())
            # df.to_csv(f"{season.value}.csv", index=False)
            logger.info(f"DataFrame written to CSV. File: '{season.value}.csv'.")
                                
        logger.info("Completed building previous seasons.")

    @staticmethod
    def build_seasons(
        seasons: PastSeasons
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
                    
                    games = execution_context.client.schedule.team_season_schedule(team, season.value)["games"]
                    logger.info(f"Found '{len(games)}' games for team '{team}' in season '{season.value}'.")
                    
                    Builder.process_team(games, games_processed, data)
                    
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
    def build_past_seasons():
        logger.info("Start building past seasons.")
        Builder.build_seasons(PastSeasons.items(), summarizer)
        logger.info("Completed building previous seasons.")
    
    @staticmethod
    def build_current_season():
        # TODO: We should short-circuit and skip trying to prcess future games already in the system.
        # Avoid multiple rows for a single game by recoding the IDs for games already processed.
        games_processed = []
        data = []
        
        for team in TeamMap:
            try:
                logger.info(f"Start processing for team '{team}' in season '{CurrentSeason}'.")
                
                games = execution_context.client.schedule.team_season_schedule(team, CurrentSeason)["games"]
                logger.info(f"Found '{len(games)}' games for team '{team}' in season '{CurrentSeason}'.")
                
                Builder.process_team(games, games_processed, data)
                
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
    def process_team_db(games_raw, data):
        games_db = data[DB.games_table_name]

        try:
            for game in games_raw:
                try:
                    if game[Keys.id] in games_db:
                        logger.info(f"Skipping game '{game[Keys.id]}' which was already processed.")
                        continue
                    if GameType(game[Keys.game_type]) not in SupportedGameTypes:
                        logger.info(f"Skipping game '{game[Keys.id]}' which is not a supported game type. Type: '{game[Keys.game_type]}'.")
                        continue

                    # game ID is the primary key for the games DB
                    games_db[game[Keys.id]] = {
                        Keys.season: game[Keys.season],
                        Keys.game_type: game[Keys.game_type],
                        Keys.game_state: game[Keys.game_state]
                    }

                    box_score = execution_context.client.game_center.boxscore(game[Keys.id])

                    Builder.process_box_score_db(box_score, data)

                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(f"Exception processing box_score query. Exception: '{str(e)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

        except Exception as e:
            print("\033[31mException occured. Check logs.\033[0m")
            logger.exception(f"Exception processing team_season_schedule query. Exception: '{str(e)}', games: '{json.dumps(games_raw, indent=4)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

    @staticmethod
    def process_team(games, games_processed, data):
        try:
            for game in games:
                try:
                    if game["id"] in games_processed:
                        logger.info(f"Skipping game '{game["id"]}' which was already processed.")
                        continue
                    games_processed.append(game["id"])
                    box_score = execution_context.client.game_center.boxscore(game["id"])
                    if box_score["gameType"] != GameType.RegularSeason.value:
                        logger.info(f"Skipping game '{game["id"]}' which is not a regular season game.")
                        continue
                    
                    data.append(Builder.process_game(box_score))

                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(f"Exception processing box_score query. Exception: '{str(e)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

        except Exception as e:
            print("\033[31mException occured. Check logs.\033[0m")
            logger.exception(f"Exception processing team_season_schedule query. Exception: '{str(e)}', games: '{json.dumps(games, indent=4)}', box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True)

    @staticmethod
    def process_box_score_db(box_score, data):
        logger.info("Processing players.")
        
        if Keys.player_by_game_stats not in box_score:
            logger.warning("Roster not published yet")
            return None
        
        home_team = utl.json_value_or_default(box_score, Keys.player_by_game_stats, Keys.home_team)
        away_team = utl.json_value_or_default(box_score, Keys.player_by_game_stats, Keys.away_team)

        Builder.process_skaters_db(home_team[Keys.forwards] + home_team[Keys.defense], data, utl.json_value_or_default(box_score, Keys.id))
        Builder.process_goalies_db(home_team[Keys.goalies], data, utl.json_value_or_default(box_score, Keys.id))
        Builder.process_skaters_db(away_team[Keys.forwards] + away_team[Keys.defense], data, utl.json_value_or_default(box_score, Keys.id))
        Builder.process_goalies_db(away_team[Keys.goalies], data, utl.json_value_or_default(box_score, Keys.id))

        logger.info("Players processed.")

    @staticmethod
    def process_skaters_db(skaters, data, game_id):
        skater_stats_db = data[DB.skater_stats_table_name]

        for skater in skaters:
            skater_stats_db[len(skater_stats_db)+1] = {
                Keys.game_id: game_id,
                Keys.player_id: utl.json_value_or_default(skater, Keys.player_id),
                Keys.goals: utl.json_value_or_default(skater, Keys.goals),
                Keys.assists: utl.json_value_or_default(skater, Keys.assists),
                Keys.points: utl.json_value_or_default(skater, Keys.points),
                Keys.plus_minus: utl.json_value_or_default(skater, Keys.plus_minus),
                Keys.pim: utl.json_value_or_default(skater, Keys.pim),
                Keys.hits: utl.json_value_or_default(skater, Keys.hits),
                Keys.power_play_goals: utl.json_value_or_default(skater, Keys.power_play_goals),
                Keys.sog : utl.json_value_or_default(skater, Keys.sog),
                Keys.faceoff_winning_pctg: utl.json_value_or_default(skater, Keys.faceoff_winning_pctg),
                Keys.toi: utl.json_value_or_default(skater, Keys.toi),
                Keys.blocked_shots: utl.json_value_or_default(skater, Keys.blocked_shots),
                Keys.shifts: utl.json_value_or_default(skater, Keys.shifts),
                Keys.giveaways: utl.json_value_or_default(skater, Keys.giveaways),
                Keys.takeaways: utl.json_value_or_default(skater, Keys.takeaways)
            }

    @staticmethod
    def process_goalies_db(goalies, data, game_id):
        goalie_stats_db = data[DB.goalie_stats_table_name]

        for goalie in goalies:
            goalie_stats_db[len(goalie_stats_db)+1] = {
                Keys.game_id: game_id,
                Keys.player_id: utl.json_value_or_default(goalie, Keys.player_id),
                Keys.even_strength_shots_against: utl.json_value_or_default(goalie, Keys.even_strength_shots_against),
                Keys.power_play_shots_against: utl.json_value_or_default(goalie, Keys.power_play_shots_against),
                Keys.shorthanded_shots_against: utl.json_value_or_default(goalie, Keys.power_play_shots_against),
                Keys.save_shots_against: utl.json_value_or_default(goalie, Keys.save_shots_against),
                Keys.save_pctg: utl.json_value_or_default(goalie, Keys.save_pctg),
                Keys.even_strength_goals_against: utl.json_value_or_default(goalie, Keys.even_strength_goals_against),
                Keys.power_play_goals_against: utl.json_value_or_default(goalie, Keys.power_play_goals_against),
                Keys.shorthanded_goals_against: utl.json_value_or_default(goalie, Keys.shorthanded_goals_against),
                Keys.pim: utl.json_value_or_default(goalie, Keys.pim),
                Keys.goals_against: utl.json_value_or_default(goalie, Keys.goals_against),
                Keys.toi: utl.json_value_or_default(goalie, Keys.toi),
                Keys.starter: utl.json_value_or_default(goalie, Keys.starter),
                Keys.decision: utl.json_value_or_default(goalie, Keys.decision),
                Keys.shots_against: utl.json_value_or_default(goalie, Keys.shots_against),
                Keys.saves: utl.json_value_or_default(goalie, Keys.saves)
            }

    @staticmethod
    def process_game(box_score):
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
    def process_game_historical(box_score, use_season_totals):
        logger.info("Summarizing rosters with historical data.")
        if "playerByGameStats" not in box_score:
            logger.warning("Roster not published yet")
            return None

        summary = summarizer.summarize_historical(
            box_score["playerByGameStats"]["homeTeam"],
            box_score["playerByGameStats"]["awayTeam"],
            use_season_totals # TODO: Check on this
        )
        logger.info("Rosters summarized.")

        entry = GameEntry.from_json(box_score)
        entry.add_roster(*summary)

        logger.info(f"Adding game entry to data set: '{entry}'.")
        return repr(entry).split(',')