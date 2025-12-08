import json
import sys

from nhlpy import NHLClient

import shared.execution_context
from model.player_info import GoalieInfo, SkaterInfo
from shared.constants.json import JSON as Keys
from shared.logging_config import LoggingConfig

logger = LoggingConfig.get_logger(__name__)
execution_context = shared.execution_context.ExecutionContext()

class AveragePlayerSummarizer:

    def get_file_name():
        return "AverageSummarizer"

    def summarize(self, homeRoster, awayRoster):
        logger.info("Summarizing home and away rosters.")
        homeSummary = self.summarize_roster(homeRoster)
        awaySummary = self.summarize_roster(awayRoster)

        return homeSummary, awaySummary

    def summarize_db(self, homeRoster, awayRoster):
        logger.info("Summarizing home and away rosters.")
        homeSummary = self.summarize_roster_db(homeRoster)
        awaySummary = self.summarize_roster_db(awayRoster)

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
        
        print(json.dumps(roster, indent=4))
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
        print(json.dumps(result, indent=4))
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