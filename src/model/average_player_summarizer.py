import json
import sys

import pandas as pd

import shared.execution_context
from model.player_info import GoalieInfo, SkaterInfo
from shared.constants.database import Database as DB
from shared.constants.json import JSON as Keys
from shared.logging_config import LoggingConfig

logger = LoggingConfig.get_logger(__name__)
execution_context = shared.execution_context.ExecutionContext()

class AveragePlayerSummarizer:

    def get_file_name():
        return "AverageSummarizer"
    
    def summarize_db(self, data):
        self.cleanup_data_db(data)
        skater_summary_by_game, goalie_summary_by_game = self.reduce_data_db(data)
        game_stats = pd.merge(
            skater_summary_by_game,
            goalie_summary_by_game,
            how='outer',
            on=Keys.game_id)
        #TODO game_stats[Keys.winner] = <calculate winner column>
        
        return game_stats

    
    def cleanup_data_db(self, data):
        skaters_db = data[DB.skater_stats_table_name]
        goalies_db = data[DB.goalie_stats_table_name]

        # TODO: Fix build-stage bug introducing duplicates then remove this.
        skaters_db = skaters_db.groupby([Keys.game_id, Keys.player_id]).first()
        goalies_db = goalies_db.groupby([Keys.game_id, Keys.player_id]).first()

        # Clean up the skaters_db column datatypes
        skaters_db = skaters_db.astype({
            Keys.toi: "string",
        })

        # The shot columns provide us with shots againsts, saves against and goals
        # against. Since saves + goals = shots, this may be too much information.
        # There are several columns like this that may be introducing duplicates
        # when split.
        # TODO: Need to unpack if these relationships are bad for the model.
        goalies_db[[Keys.even_strength_saves_against, Keys.even_strength_shots_against]] = goalies_db[Keys.even_strength_shots_against].str.split('/', expand=True)
        goalies_db[[Keys.power_play_saves_against, Keys.power_play_shots_against]] = goalies_db[Keys.power_play_shots_against].str.split('/', expand=True)
        goalies_db[[Keys.shorthanded_saves_against, Keys.shorthanded_shots_against]] = goalies_db[Keys.shorthanded_shots_against].str.split('/', expand=True)
        goalies_db[[Keys.save_saves_against, Keys.save_shots_against]] = goalies_db[Keys.save_shots_against].str.split('/', expand=True)

        # Clean up the goalies_db column datatypes
        goalies_db = goalies_db.astype({
            Keys.even_strength_shots_against: int,
            Keys.power_play_shots_against: int,
            Keys.shorthanded_shots_against: int,
            Keys.save_shots_against: int,
            Keys.toi: "string",
            Keys.decision: "string",
            Keys.even_strength_saves_against: int,
            Keys.power_play_saves_against: int,
            Keys.shorthanded_saves_against: int,
            Keys.save_saves_against: int
        })

        data[DB.skater_stats_table_name] = skaters_db
        data[DB.goalie_stats_table_name] = goalies_db



    def reduce_data_db(self, data):
        # TODO: Need to split players by team before summarizing
        games_db = data[DB.games_table_name]
        skaters_db = data[DB.skater_stats_table_name]
        goalies_db = data[DB.goalie_stats_table_name]

        skaters_grouped = skaters_db.groupby(Keys.game_id)
        skaters_reduced = pd.DataFrame({
            Keys.goals: skaters_grouped[Keys.goals].sum(),
            Keys.assists: skaters_grouped[Keys.assists].sum(),
            Keys.points: skaters_grouped[Keys.points].sum(),
            Keys.plus_minus: skaters_grouped[Keys.plus_minus].sum(),
            # PIM TODO
            Keys.hits: skaters_grouped[Keys.hits].sum(),
            Keys.power_play_goals: skaters_grouped[Keys.power_play_goals].sum(),
            Keys.sog: skaters_grouped[Keys.sog].sum(),
            # faceoffWinningPctg TODO
            # TOI TODO
            Keys.blocked_shots: skaters_grouped[Keys.blocked_shots].sum(),
            Keys.shifts: skaters_grouped[Keys.shifts].sum(),
            Keys.giveaways: skaters_grouped[Keys.giveaways].sum(),
            Keys.takeaways: skaters_grouped[Keys.takeaways].sum()
        })

        goalies_grouped = goalies_db.groupby(Keys.game_id)
        goalies_reduced = pd.DataFrame({
            Keys.even_strength_shots_against: goalies_grouped[Keys.even_strength_shots_against].sum(),
            Keys.power_play_shots_against: goalies_grouped[Keys.power_play_shots_against].sum(),
            Keys.shorthanded_shots_against: goalies_grouped[Keys.shorthanded_shots_against].sum(),
            Keys.save_shots_against: goalies_grouped[Keys.save_shots_against].sum(),
            #Keys.save_pctg: goalies_grouped.apply(lambda x: (x[Keys.saves]/x[Keys.shots_against])) TODO
            Keys.even_strength_goals_against: goalies_grouped[Keys.even_strength_goals_against].sum(),
            Keys.power_play_goals_against: goalies_grouped[Keys.power_play_goals_against].sum(),
            Keys.shorthanded_goals_against: goalies_grouped[Keys.shorthanded_goals_against].sum(),
            Keys.pim: goalies_grouped[Keys.pim].sum(),
            Keys.goals_against: goalies_grouped[Keys.goals_against].sum(),
            #TOI TODO
            #starter TODO
            #decision TODO
            Keys.shots_against: goalies_grouped[Keys.shots_against].sum(),
            Keys.saves: goalies_grouped[Keys.saves].sum(),
            Keys.even_strength_saves_against: goalies_grouped[Keys.even_strength_saves_against].sum(),
            Keys.power_play_saves_against: goalies_grouped[Keys.power_play_saves_against].sum(),
            Keys.shorthanded_saves_against: goalies_grouped[Keys.shorthanded_saves_against].sum(),
            Keys.save_saves_against: goalies_grouped[Keys.save_saves_against].sum(),
        })

        return skaters_reduced, goalies_reduced


    def summarize(self, homeRoster, awayRoster):
        logger.info("Summarizing home and away rosters.")
        homeSummary = self.summarize_roster(homeRoster)
        awaySummary = self.summarize_roster(awayRoster)

        return homeSummary, awaySummary

    def summarize_historical(self, homeRoster, awayRoster, use_season_totals):
        logger.info("Summarizing home and away rosters.")
        homeSummary = self.summarize_roster(
            AveragePlayerSummarizer.historical_transform(homeRoster, use_season_totals)
            )
        awaySummary = self.summarize_roster(
            AveragePlayerSummarizer.historical_transform(awayRoster, use_season_totals)
            )

        return homeSummary, awaySummary

    def historical_transform(roster, use_season_totals):
        # TODO: Actually implement this
        logger.info("Summarizing home and away rosters with historical data.")
        
        for player in roster["forwards"]:
            AveragePlayerSummarizer.get_historical_stats_for_player(
                player["playerId"],
                use_season_totals
            )
        for player in roster["defense"]:
            AveragePlayerSummarizer.get_historical_stats_for_player(
                player["playerId"],
                use_season_totals
            )
        for player in roster["goalies"]:
            AveragePlayerSummarizer.get_historical_stats_for_player(
                player["playerId"],
                use_season_totals
            )
        
        return roster
    
    def get_historical_stats_for_player(player_id, use_season_totals):
        player_id = 8478402  #TODO: Remove
        key = "seasonTotals" if use_season_totals else "careerTotals"
        stats = execution_context.client.stats.player_career_stats(player_id)
        stats = stats[key]["regularSeason"] # TODO: Do season stats have the exact same format?
        total_games = stats["gamesPlayed"]
        # TODO: Need to ensure that historical data has parity with statistical factors
        result = {
            "playerId": player_id,
            "goals": stats["goals"]/total_games,
            "assists": stats["assists"]/total_games,
            "points": stats["points"]/total_games,
            "plusMinus": stats["plusMinus"]/total_games,
            "pim": stats["pim"]/total_games,
            #"hits": stats[""],
            "powerPlayGoals": stats["powerPlayGoals"]/total_games,
            "sog": stats["shots"]/total_games,
            "faceoffWinningPctg": stats["faceoffWinningPctg"],
            "toi": stats["avgToi"],
            #"blockedShots": stats[""],
            #"shifts": 17,
            #"giveaways": 1,
            #"takeaways": 0
        }
        sys.exit(0)

    def summarize_roster(self, roster):
        logger.info(f"Summarizing roster. Roster: '{roster}'.")
        forwards = self.summarize_skaters(roster["forwards"])
        defense = self.summarize_skaters(roster["defense"])
        goalies = self.summarize_goalies(roster["goalies"])
        return f"{forwards},{defense},{goalies}"

    def summarize_roster_db(self, roster):
        logger.info(f"Summarizing roster. Roster: '{roster}'.")
        forwards = self.summarize_skaters_db(roster["forwards"])
        defense = self.summarize_skaters_db(roster["defense"])
        goalies = self.summarize_goalies_db(roster["goalies"])
        return {  Keys.forwards: forwards, Keys.defense: defense, Keys.goalies: goalies}

    def summarize_skaters(self, players):
        logger.info(f"Summarizing skaters. Skaters: '{players}'.")
        player_objects = []
        for player in players:
            player_objects.append(SkaterInfo.from_json(player))

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
            logger.info(f"Adding skater to summary. Goalie: '{player}'.")
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
        summary = SkaterInfo(
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

        logger.info(f"Summarized goalies. Summary: '{summary}'.")
        return repr(summary)

    def summarize_skaters_db(self, players):
        logger.info(f"Summarizing skaters. Skaters: '{players}'.")
        player_objects = []
        for player in players:
            player_objects.append(SkaterInfo.from_json(player))

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
            logger.info(f"Adding skater to summary. Goalie: '{player}'.")
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
        summary = SkaterInfo(
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

        logger.info(f"Summarized goalies. Summary: '{summary}'.")
        return summary

    def summarize_goalies(self, players):
        logger.info(f"Summarizing goalies. Goalies: '{players}'.")
        player_objects = []
        for player in players:
            player_objects.append(GoalieInfo.from_json(player))

        count = 0
        es_shots_against = 0
        es_saves = 0
        pp_shots_against = 0
        pp_saves = 0
        sh_shots_against = 0
        sh_saves = 0
        save_shots_against = 0
        save_pct = 0
        es_goals_against = 0
        pp_goals_against = 0
        sh_goals_against = 0
        pim = 0
        goals_against = 0
        toi = 0
        # starter = 0
        # decision = 0
        shots_against = 0
        saves = 0

        for player in player_objects:
            logger.info(f"Adding goalie to summary. Goalie: '{player}'.")
            count += 1
            es_shots_against += player.es_shots_against
            es_saves += player.es_saves
            pp_shots_against += player.pp_shots_against
            pp_saves += player.pp_saves
            sh_shots_against += player.sh_shots_against
            sh_saves += player.sh_saves
            save_shots_against += player.save_shots_against
            save_pct += player.save_pct
            es_goals_against += player.es_goals_against
            pp_goals_against += player.pp_goals_against
            sh_goals_against += player.sh_goals_against
            pim += player.pim
            goals_against += player.goals_against
            toi += player.toi
            # starter += player.starter
            # decision += player.decision
            shots_against += player.shots_against
            saves += player.saves

        # TODO: can't just average the FO %, it needs to be weighted
        summary = GoalieInfo(
            es_shots_against,
            es_saves,
            pp_shots_against,
            pp_saves,
            sh_shots_against,
            sh_saves,
            save_shots_against,
            save_pct,
            es_goals_against,
            pp_goals_against,
            sh_goals_against,
            pim,
            goals_against,
            toi,
            # starter,
            # decision,
            shots_against,
            saves
        )

        logger.info(f"Summarized goalies. Summary: '{summary}'.")
        return repr(summary)

    def summarize_goalies_db(self, players):
        logger.info(f"Summarizing goalies. Goalies: '{players}'.")
        player_objects = []
        for player in players:
            player_objects.append(GoalieInfo.from_json(player))

        count = 0
        es_shots_against = 0
        es_saves = 0
        pp_shots_against = 0
        pp_saves = 0
        sh_shots_against = 0
        sh_saves = 0
        save_shots_against = 0
        save_pct = 0
        es_goals_against = 0
        pp_goals_against = 0
        sh_goals_against = 0
        pim = 0
        goals_against = 0
        toi = 0
        # starter = 0
        # decision = 0
        shots_against = 0
        saves = 0

        for player in player_objects:
            logger.info(f"Adding goalie to summary. Goalie: '{player}'.")
            count += 1
            es_shots_against += player.es_shots_against
            es_saves += player.es_saves
            pp_shots_against += player.pp_shots_against
            pp_saves += player.pp_saves
            sh_shots_against += player.sh_shots_against
            sh_saves += player.sh_saves
            save_shots_against += player.save_shots_against
            save_pct += player.save_pct
            es_goals_against += player.es_goals_against
            pp_goals_against += player.pp_goals_against
            sh_goals_against += player.sh_goals_against
            pim += player.pim
            goals_against += player.goals_against
            toi += player.toi
            # starter += player.starter
            # decision += player.decision
            shots_against += player.shots_against
            saves += player.saves

        # TODO: can't just average the FO %, it needs to be weighted
        summary = GoalieInfo(
            es_shots_against,
            es_saves,
            pp_shots_against,
            pp_saves,
            sh_shots_against,
            sh_saves,
            save_shots_against,
            save_pct,
            es_goals_against,
            pp_goals_against,
            sh_goals_against,
            pim,
            goals_against,
            toi,
            # starter,
            # decision,
            shots_against,
            saves
        )

        logger.info(f"Summarized goalies. Summary: '{summary}'.")
        return summary

    """
    Labels for the dataset columns represented as a list of strings.
    """
    def get_headers(cls):
        return [
            "periods",
            "homeScore",
            "homeSOG",
            "awayScore",
            "awaySOG",
            "homeForwardGoals",
            "homeForwardAssists",
            "homeForwardPoints",
            "homeForwardPlusMinus",
            "homeForwardPIM",
            "homeForwardHits",
            "homeForwardPPG",
            "homeForwardSOG",
            "homeForwardFaceoffPct",
            "homeForwardTOI",
            "homeForwardBlockedShots",
            "homeForwardGivaways",
            "homeForwardTakeaways",
            "homeDefenseGoals",
            "homeDefenseAssists",
            "homeDefensePoints",
            "homeDefensePlusMinus",
            "homeDefensePIM",
            "homeDefenseHits",
            "homeDefensePPG",
            "homeDefenseSOG",
            "homeDefenseFaceoffPct",
            "homeDefenseTOI",
            "homeDefenseBlockedShots",
            "homeDefenseGivaways",
            "homeDefenseTakeaways",
            "homeGoalieEvenStrengthShotsAgainst",
            "homeGoalieEvenStrengthSaves",
            "homeGoaliePowerPlayShotsAgainst",
            "homeGoaliePowerPlaySaves",
            "homeGoalieShortHandedShotsAgainst",
            "homeGoalieShortHandedSaves",
            "homeGoalieSaveShotsAgainst",
            "homeGoalieSavePct",
            "homeGoalieEvenStrengthGoalsAgainst",
            "homeGoaliePowerPlayGoalsAgainst",
            "homeGoalieShortHandedGoalsAgainst",
            "homeGoaliePIM",
            "homeGoalieGoalsAgainst",
            "homeGoalieTOI",
            "homeGoalieShotsAgainst",
            "homeGoalieSaves",
            "awayForwardGoals",
            "awayForwardAssists",
            "awayForwardPoints",
            "awayForwardPlusMinus",
            "awayForwardPIM",
            "awayForwardHits",
            "awayForwardPPG",
            "awayForwardSOG",
            "awayForwardFaceoffPct",
            "awayForwardTOI",
            "awayForwardBlockedShots",
            "awayForwardGivaways",
            "awayForwardTakeaways",
            "awayDefenseGoals",
            "awayDefenseAssists",
            "awayDefensePoints",
            "awayDefensePlusMinus",
            "awayDefensePIM",
            "awayDefenseHits",
            "awayDefensePPG",
            "awayDefenseSOG",
            "awayDefenseFaceoffPct",
            "awayDefenseTOI",
            "awayDefenseBlockedShots",
            "awayDefenseGivaways",
            "awayDefenseTakeaways",
            "awayGoalieEvenStrengthShotsAgainst",
            "awayGoalieEvenStrengthSaves",
            "awayGoaliePowerPlayShotsAgainst",
            "awayGoaliePowerPlaySaves",
            "awayGoalieShortHandedShotsAgainst",
            "awayGoalieShortHandedSaves",
            "awayGoalieSaveShotsAgainst",
            "awayGoalieSavePct",
            "awayGoalieEvenStrengthGoalsAgainst",
            "awayGoaliePowerPlayGoalsAgainst",
            "awayGoalieShortHandedGoalsAgainst",
            "awayGoaliePIM",
            "awayGoalieGoalsAgainst"
            "awayGoalieTOI",
            "awayGoalieShotsAgainst",
            "awayGoalieSaves",
            "winnerHomeOrAway"
        ]