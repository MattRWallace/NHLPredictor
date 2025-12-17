from typing import Dict

import pandas as pd
from sqlitedict import SqliteDict

from model.home_or_away import HomeOrAway
from model.summarizers.summarizer import Summarizer
from shared.constants.database import Database as DB
from shared.constants.json import JSON as Keys
from shared.logging_config import LoggingConfig

logger = LoggingConfig.get_logger(__name__)

class AveragePlayerSummarizer(Summarizer):
    """Summarizer that simply averages or sums, as appropriate, each statistic
    across a game roster.
    """

    def get_filename_prefix() -> str:
        """Returns a prefix for naming the model save file with.

        Returns:
            str: File name prefix.
        """
        return "AverageSummarizer"
    
    def summarize(
        self,
        data: Dict[str, SqliteDict]
    ) -> pd.DataFrame:
        """Creates a single DataFrame containing the data set.

        Args:
            data (Dict[str, SqliteDict]): Collection of raw data.

        Returns:
            pd.DataFrame: Data set.
        """
        self._cleanup_data(data)
        return self._reduce_data(data)

    def _cleanup_data(
        self,
        data: Dict[str, SqliteDict]
    ) -> None:
        """Cleans up the data to prepare for processing.

        Args:
            data (Dict[str, SqliteDict]): Collection of raw data.
        """
        skaters_db = data[DB.skater_stats_table_name]
        goalies_db = data[DB.goalie_stats_table_name]

        # TODO: Fix build-stage bug introducing duplicates then remove this.
        skaters_db = skaters_db.groupby([Keys.game_id, Keys.player_id]).first().reset_index()
        goalies_db = goalies_db.groupby([Keys.game_id, Keys.player_id]).first().reset_index()
        
        skaters_db = self._fix_skater_column_dtypes(skaters_db)
        self._split_compound_goalie_stats(goalies_db)
        goalies_db = self._fix_goalie_column_dtypes(goalies_db)

        data[DB.skater_stats_table_name] = skaters_db
        data[DB.goalie_stats_table_name] = goalies_db

    def _fix_skater_column_dtypes(
        skaters: pd.DataFrame
    ) -> pd.DataFrame:
        """Corrects the column dtypes for skater data.

        Args:
            skaters (pd.DataFrame): Raw skater data.

        Returns:
            pd.DataFrame: DataFrame with corrected column dtypes.
        """
        return skaters.astype({
            Keys.toi: "string",
        })
    
    def _fix_goalie_column_dtypes(
        goalies: pd.DataFrame
    ) -> pd.DataFrame:
        """Corrects the column dtypes for goalie data.

        Args:
            goalies (pd.DataFrame): Raw goalie data.

        Returns:
            pd.DataFrame: DataFrame with corrected column dtypes.
        """
        return goalies.astype({
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
    
    # The shot columns provide us with shots againsts, saves against and goals
    # against. Since saves + goals = shots, this may be too much information.
    # There are several columns like this that may be introducing duplicates
    # when split.
    # TODO: Need to unpack if these relationships are bad for the model.
    def _split_compound_goalie_stats(
        goalies: pd.DataFrame
    ) -> None:
        """Splits columns with compound values into individual columns. Changes are made in place.

        Args:
            goalies (pd.DataFrame): Raw goalie data.
        """
        goalies[[Keys.even_strength_saves_against, Keys.even_strength_shots_against]] = \
            goalies[Keys.even_strength_shots_against].str.split('/', expand=True)
        goalies[[Keys.power_play_saves_against, Keys.power_play_shots_against]] = \
            goalies[Keys.power_play_shots_against].str.split('/', expand=True)
        goalies[[Keys.shorthanded_saves_against, Keys.shorthanded_shots_against]] = \
            goalies[Keys.shorthanded_shots_against].str.split('/', expand=True)
        goalies[[Keys.save_saves_against, Keys.save_shots_against]] = \
            goalies[Keys.save_shots_against].str.split('/', expand=True)

    def _reduce_data(
        self,
        data: Dict[str, SqliteDict]
    ) -> pd.DataFrame:
        """Reduce player stats down to roster stats.

        Args:
            data (Dict[str, SqliteDict]): Collection of raw data.

        Returns:
            pd.DataFrame: DataFrame containing the stats reduced to roster granularity.
        """
        game_stats = self._flatten_all_stats(data)
        game_stats = self._add_wins_column(data, game_stats)
        return game_stats

    def _flatten_all_stats(
        self,
        data: Dict[str, SqliteDict]
    ) -> pd.DataFrame:
        """Completely flatten player stats into roster summarized stats.

        Args:
            data (Dict[str, SqliteDict]): Collection of raw data.

        Returns:
            pd.DataFrame: DataFrame with fully flattened stats.
        """
        skaters_db = data[DB.skater_stats_table_name]
        skaters_reduced = self._group_and_flatten_skater_stats(skaters_db)
        skaters_reduced = self._flatten_home_and_away(skaters_reduced, Keys.skater_prefix)
        
        goalies_db = data[DB.goalie_stats_table_name]
        goalies_reduced = self._group_and_flatten_goalie_stats(goalies_db)
        goalies_reduced = self._flatten_home_and_away(goalies_reduced, Keys.goalie_prefix)        

        return pd.merge(
            skaters_reduced,
            goalies_reduced,
            how='outer',
            on=Keys.game_id
        )

    def _add_wins_column(
        self,
        data: Dict[str, SqliteDict],
        game_stats: pd.DataFrame
    ) -> pd.DataFrame:
        """Add winner column to the data set DataFrame

        Args:
            data (Dict[str, SqliteDict]): Collection of raw data.
            game_stats (pd.DataFrame): Data set DataFrame

        Returns:
            pd.DataFrame: DataFrame joining the data set DataFrame with the winner data.
        """
        games_db = data[DB.games_table_name]
        games_db.index.name = Keys.game_id # TODO: We should fix this on the build side
        wins = pd.DataFrame(games_db[Keys.winner])
        wins.index = wins.index.astype(int)
        return pd.merge(
            game_stats,
            wins,
            how='left',
            on=Keys.game_id
        )
    
    def _group_and_flatten_skater_stats(
        skaters_db: pd.DataFrame
    ) -> pd.DataFrame:
        """Groups stats entries by game and then flattens skater stats into single stat line.

        Args:
            skaters_db (pd.DataFrame): Skater data.

        Returns:
            pd.DataFrame: DataFrame with skater stats summarized by game.
        """
        skaters_grouped = skaters_db.groupby([Keys.game_id, Keys.team_id, Keys.team_role])
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
        
        return skaters_reduced.reset_index()
        
    def _group_and_flatten_goalie_stats(
        goalies_db: pd.DataFrame
    ) -> pd.DataFrame:
        """Groups stats entries by game and then flatten goalie stats into single stat line.

        Args:
            goalies_db (pd.DataFrame): Goalie data.

        Returns:
            pd.DataFrame: DataFrame with goalie stats summarized by game.
        """
        goalies_grouped = goalies_db.groupby([Keys.game_id, Keys.team_id, Keys.team_role])
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
        
        return goalies_reduced.reset_index()

    def _flatten_home_and_away(
        data: pd.DataFrame,
        prefix: str
    ) -> pd.DataFrame:
        """Splits provided data by HOME or AWAY designation and combines the stats into a single game line using provided prefix.

        Args:
            data (pd.DataFrame): DataFrame of data to be flattened.
            prefix (str): Stat type column name prefix.

        Returns:
            pd.DataFrame: DataFrame with HOME and AWAY rows joined.
        """
        home = (
            data[data[Keys.team_role] == HomeOrAway.HOME.value]
            .drop([Keys.team_role, Keys.team_id], axis=1)
        )
        away = (
            data[data[Keys.team_role] == HomeOrAway.AWAY.value]
            .drop([Keys.team_role, Keys.team_id], axis=1)
        )
        return pd.merge(
            home,
            away,
            how='outer',
            on=Keys.game_id,
            suffixes=(Keys.home_suffix, Keys.away_suffix)
        ).set_index(Keys.game_id).add_prefix(prefix)