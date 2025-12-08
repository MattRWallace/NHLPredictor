import os
from pathlib import Path

from sqlitedict import SqliteDict


class Utility:
    """
    Check the json_data for a value associated with the provided key.  If no
    such key exists, return the default value instead.

    TODO: Use dictionary unpacking to manage multiple indexing.
    TODO: Update all the dictionary indexing with this method.
    """
    @staticmethod
    def json_value_or_default(json_data, *keys, default=0):
        try:
            value = json_data
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            # TODO: Log
            return default

    """
    Takes a 2 dimensional list of strings and prints the contents out in the form
    of a table.
    
    Values must be of type string or method will throw.
    """   
    @staticmethod
    def print_table(table, align="", hasHeader=False, pad=2, isGrid=False):
        table = [row[:] for row in table] # copy table
        numRows, numCols = len(table), len(table[0]) # table size
        align = align.ljust(numCols,"L") # align left by default
        align = ["RC".find(c)+1 for c in align] # convert to index (?RC=012)
        widths = [max(len(row[col]) for row in table) for col in range(numCols)] # column widths

        # --- apply column widths with alignments ---
        if hasHeader: # header is centered
            for x in range(numCols):
                table[0][x] = table[0][x].center(widths[x])
        for y in range(hasHeader, numRows): # apply column alignments
            for x in range(numCols):
                c = table[y][x]
                table[y][x] = [c.ljust, c.rjust, c.center][align[x]](widths[x])

        # --- data for printing
        P = " "*pad
        LSEP,SEP,RSEP = "│"+P, P+"│"+P, P+"│"
        lines = ["─"*(widths[col]+pad*2) for col in range(numCols)]

        drawLine = [isGrid]*numRows
        drawLine[0]|=hasHeader
        drawLine[-1] = False
        if hasHeader or isGrid:
            gridLine = "├"+"┼".join(lines)+"┤" # if any(drawLine)

        # --- print rows ---
        print("┌"+"┬".join(lines)+"┐")
        for y in range(numRows):
            print(LSEP+SEP.join(table[y])+RSEP)
            if drawLine[y]:
                print(gridLine)
        print("└"+"┴".join(lines)+"┘")

    @staticmethod
    def get_db_path(path: Path):
        return os.path.join(path, "NHLPredictor.sqlite")
    
    """
    Some goalies stats are represented as a save/try pair.  For example, see
    shots against stats that are shown like 21/27 where 21 is the number of
    saves and 27 is the total attempts.
    """
    @staticmethod
    def split_save_try_pair(value):
        parts = str(value).split('/')
        parts = [int(part) for part in parts]

        return tuple(parts)

    @staticmethod
    def get_db_connections(
        *names,
        path: Path,
        update_db: bool = False,
        read_only: bool = False
    ):
        DBs = {}
        if update_db:
            # Empty the database on open
            flag = "w"
        else:
            # Open for read/write without modification
            flag = "c"
        if read_only:
            # Process readonly flag last as we want it to take precedence.
            flag = "r"

        for name in names:
            DBs[name] = SqliteDict(
                Utility.get_db_path(path),
                tablename=name,
                autocommit=True,
                flag=flag
            )
        return DBs