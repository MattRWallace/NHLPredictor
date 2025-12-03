import json
from typing import List

import pandas as pd

import shared.execution_context
from model.game_state import GameState, GameStatesForDataset
from model.game_type import GameType, SupportedGameTypes
from model.seasons import CurrentSeason, PastSeasons
from model.team_map import TeamMap
from shared.constants.database import Database as DB
from shared.constants.json import JSON as Keys
from shared.logging_config import LoggingConfig
from shared.utility import Utility as utl

logger = LoggingConfig.get_logger(__name__)
execution_context = shared.execution_context.ExecutionContext()

class Builder:
    
    @staticmethod
    def build(
        seasons,
        all_seasons: bool = False
    ):
        # TODO: With the new design, does it makes sense to expose season
        # selection to the end user? Should we just always do all games?
        if all_seasons:
            Builder.build_seasons()
            Builder.build_current_season()
        elif seasons is not None:
            Builder.build_seasons(seasons)
        else:
            logger.error("Invalid season specification, cannot build data set.")
        logger.info("Call to build_games is complete.")
    
    @staticmethod
    def report():
        pass

    @staticmethod
    def build_seasons(
        seasons: List[str] = [x.value for  x in PastSeasons.items()],
    ):
        logger.info("Start building seasons.")

        # TODO: What are the implications of the design change on the 'update'
        # parameter? Are there changes to how we connect to the DB?
        data = utl.get_db_connections(
            DB.players_table_name,
            DB.skater_stats_table_name,
            DB.goalie_stats_table_name,
            DB.games_table_name
        )
        
        for season in seasons:
            logger.info(f"Start of processing for season '{season}'.")

            for team in TeamMap:
                logger.info(f"Start processing for team '{team}' in season '{season}'.")
                try:
                    games_raw = execution_context.client.schedule.team_season_schedule(team, season)[Keys.games]
                    logger.info(f"Found '{len(games_raw)}' games for team '{team}' in season '{season}'.")
                    Builder.process_team_games(games_raw, data)
                    logger.info(f"Completed processing games for team. Team:'{team}'.")
                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(
                        f"Exception processing team_season_schedule query. "
                        f"Games: '{json.dumps(games_raw, indent=4)}',"
                        f"Exception: '{str(e)}'.",
                        stack_info=True)

        # TODO: Factor this out into a method
        skaters_db = data[DB.skater_stats_table_name]
        goalies_db = data[DB.goalie_stats_table_name]
        player_ids = set()
        for record in skaters_db:
            player_ids.add(skaters_db[record][Keys.player_id])
        for record in goalies_db:
            player_ids.add(goalies_db[record][Keys.player_id])
        
        Builder.process_players(player_ids, data)

    @staticmethod
    def build_current_season():
        Builder.build_seasons([CurrentSeason])
    
    @staticmethod
    def process_team_games(games_raw, data):
        games_db = data[DB.games_table_name]

        try:
            for game in games_raw:
                try:
                    if game[Keys.id] in games_db:
                        logger.info(
                            f"Skipping game '{game[Keys.id]}' which was already "
                            "processed."
                        )
                        continue
                    if (GameType(utl.json_value_or_default(game, Keys.game_type, default=GameType.Preseason))
                        not in SupportedGameTypes):
                        logger.info(
                            f"Skipping game '{game[Keys.id]}' which is not a "
                            f"supported game type. Type: '{game[Keys.game_type]}'."
                        )
                        continue
                    if (GameState(utl.json_value_or_default(game, Keys.game_state, default=GameState.Future))
                        not in GameStatesForDataset):
                        logger.info(
                            f"Skipping game '{game[Keys.id]}' which is not a "
                            f"supported game state. State: '{game[Keys.game_state]}'."
                        )

                    # game ID is the primary key for the games DB
                    games_db[game[Keys.id]] = {
                        Keys.season: game[Keys.season],
                        Keys.game_type: game[Keys.game_type],
                        Keys.game_state: game[Keys.game_state]
                    }
                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(
                        f"Exception adding game data to database. Exception: "
                        f"'{str(e)}'.",
                        stack_info=True
                    )

                try:
                    box_score = execution_context.client.game_center.boxscore(game[Keys.id])
                    Builder.process_box_score(box_score, data)
                except Exception as e:
                    print("\033[31mException occured. Check logs.\033[0m")
                    logger.exception(
                        f"Exception processing box_score query. Exception: "
                        f"'{str(e)}', box_score: '{json.dumps(box_score, indent=4)}'.",
                        stack_info=True
                    )

        except Exception as e:
            print("\033[31mException occured. Check logs.\033[0m")
            logger.exception(
                f"Exception processing team_season_schedule query. Exception: "
                f"'{str(e)}', games: '{json.dumps(games_raw, indent=4)}', "
                f"box_score: '{json.dumps(box_score, indent=4)}'.", stack_info=True
            )

    @staticmethod
    def process_box_score(box_score, data):
        logger.info("Processing players.")
        
        if Keys.player_by_game_stats not in box_score:
            logger.warning("Roster not published yet")
            return None
        
        home_team = utl.json_value_or_default(box_score, Keys.player_by_game_stats, Keys.home_team)
        away_team = utl.json_value_or_default(box_score, Keys.player_by_game_stats, Keys.away_team)

        Builder.process_skaters(home_team[Keys.forwards] + home_team[Keys.defense], data, utl.json_value_or_default(box_score, Keys.id))
        Builder.process_goalies(home_team[Keys.goalies], data, utl.json_value_or_default(box_score, Keys.id))
        Builder.process_skaters(away_team[Keys.forwards] + away_team[Keys.defense], data, utl.json_value_or_default(box_score, Keys.id))
        Builder.process_goalies(away_team[Keys.goalies], data, utl.json_value_or_default(box_score, Keys.id))

        # TODO: Players will only be updated when there is a game to process
        # that they participated in. Perhaps this can move up the stack and
        # get the set of players to process via unique player IDs in the stats
        # databases?
        # Builder.process_players(
        #     home_team[Keys.forwards]
        #     + home_team[Keys.defense]
        #     + home_team[Keys.goalies]
        #     + away_team[Keys.forwards]
        #     + away_team[Keys.defense]
        #     + away_team[Keys.goalies],
        #     data
        # )

        logger.info("Player stats by game processed.")

    @staticmethod
    def process_skaters(skaters, data, game_id):
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
    def process_goalies(goalies, data, game_id):
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
    def process_players(players, data):
        players_db = data[DB.players_table_name]

        for player_id in players:
            stats = execution_context.client.stats.player_career_stats(player_id)
            first_name = utl.json_value_or_default(stats, Keys.first_name, Keys.default, default="")
            last_name = utl.json_value_or_default(stats, Keys.last_name, Keys.default, default="")

            if not utl.json_value_or_default(stats, Keys.is_Active, default=False):
                logger.info(
                    f"Skipping inactive player. PlayerId: '{stats[Keys.player_id]}', "
                    f"Name: '{first_name} {last_name}'."
                )
                if player_id in players_db:
                    logger.info(
                        f"Deleting inactive player in database. "
                        f"PlayerId: '{stats[Keys.player_id]}', "
                        f"Name: '{stats[Keys.first_name]} {stats[Keys.last_name]}'."
                    )
                    del players_db[player_id]
            else:
                players_db[player_id] = {
                    Keys.current_team_id: utl.json_value_or_default(stats, Keys.current_team_id),
                    Keys.first_name: first_name,
                    Keys.last_name: last_name,
                    Keys.height_in_cm: utl.json_value_or_default(stats, Keys.height_in_cm),
                    Keys.weight_in_kg: utl.json_value_or_default(stats, Keys.weight_in_kg)
                }


    # TODO: Keep for reference while updating other modules.
    # Delete when that is complete.

    # @staticmethod
    # def process_game(box_score):
    #     logger.info("Summarizing rosters.")
    #     if "playerByGameStats" not in box_score:
    #         logger.warning("Roster not published yet")
    #         return None
    #     summary = summarizer.summarize(
    #         box_score["playerByGameStats"]["homeTeam"],
    #         box_score["playerByGameStats"]["awayTeam"]
    #     )
    #     logger.info("Rosters summarized.")
        
    #     entry = GameEntry.from_json(box_score)
    #     entry.add_roster(*summary)
        
    #     logger.info(f"Adding game entry to data set: '{entry}'.")
    #     return repr(entry).split(',')

    # @staticmethod
    # def process_game_historical(box_score, use_season_totals):
    #     logger.info("Summarizing rosters with historical data.")
    #     if "playerByGameStats" not in box_score:
    #         logger.warning("Roster not published yet")
    #         return None

    #     summary = summarizer.summarize_historical(
    #         box_score["playerByGameStats"]["homeTeam"],
    #         box_score["playerByGameStats"]["awayTeam"],
    #         use_season_totals # TODO: Check on this
    #     )
    #     logger.info("Rosters summarized.")

    #     entry = GameEntry.from_json(box_score)
    #     entry.add_roster(*summary)

    #     logger.info(f"Adding game entry to data set: '{entry}'.")
    #     return repr(entry).split(',')