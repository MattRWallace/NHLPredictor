from __future__ import annotations

from enum import Enum

import model.summarizers.average_player_summarizer as avsum


class Summarizers(str, Enum):
    average_player_summarizer = "average"

    """
    Build a summarizer instance from the specified summarizer type.
    """
    @staticmethod
    def get_summarizer(summarizer: Summarizers):
        match summarizer:
            case Summarizers.average_player_summarizer:
                return avsum.AveragePlayerSummarizer()
            case _:
                # TODO: Shouldn't throw generic Exception
                raise Exception("Unsupported summarizer specified.")