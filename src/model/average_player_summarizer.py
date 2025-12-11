import pandas as pd

import shared.execution_context
from shared.constants.database import Database as DB
from shared.constants.json import JSON as Keys
from shared.logging_config import LoggingConfig

logger = LoggingConfig.get_logger(__name__)
execution_context = shared.execution_context.ExecutionContext()

class AveragePlayerSummarizer:

    def get_file_name():
        return "AverageSummarizer"
    
    def summarize(self, data):
        self.cleanup_data(data)
        return self.reduce_data(data)

    def cleanup_data(self, data):
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

    def reduce_data(self, data):
        # TODO: break this into smaller methods
        skaters_db = data[DB.skater_stats_table_name]
        goalies_db = data[DB.goalie_stats_table_name]

        skaters_grouped = skaters_db.groupby([Keys.game_id, Keys.team_id])
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
            Keys.takeaways: skaters_grouped[Keys.takeaways].sum(),
        })

        goalies_grouped = goalies_db.groupby([Keys.game_id, Keys.team_id])
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

        skaters_reduced = skaters_reduced.reset_index()
        goalies_reduced = goalies_reduced.reset_index()
        
        # TODO: We're still managing to mingle home and away stats. Need
        # to segregate those.
        # Thought: Utilize Utility.json... to take a prefix??

        games_db = data[DB.games_table_name]
        games_db.index.name = Keys.game_id # TODO: We should fix this on the build side
        game_stats = pd.merge(
            skaters_reduced,
            goalies_reduced,
            how='outer',
            on=[Keys.game_id, Keys.team_id])
        game_stats = game_stats.set_index(Keys.game_id)
        wins = pd.DataFrame(games_db[Keys.winner])
        wins.index = wins.index.astype(int)
        game_stats = pd.merge(
            game_stats,
            wins,
            how='left',
            on=Keys.game_id
        )
        return game_stats

    """
    Labels for the dataset columns represented as a list of strings.
    TODO: Remove this after predictor is updated to use the database.
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