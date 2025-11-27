class Utility:
    """
    Check the json_data for a value associated with the provided key.  If no
    such key exists, return the default value instead.

    TODO: Does this need to be broadly available or can it be a staticmethod
    on the player_info class?
    """
    @staticmethod
    def json_value_or_default(json_data, key, default=0):
        try:
            return json_data[key]
        except KeyError:
            # TODO: Log
            return default
        
    @staticmethod
    def print_table(table,align="",hasHeader=False,pad=2,isGrid=False):
        table = [row[:] for row in table] # copy table
        numRows,numCols = len(table),len(table[0]) # table size
        align = align.ljust(numCols,"L") # align left by default
        align = ["RC".find(c)+1 for c in align] # convert to index (?RC=012)
        widths = [max(len(row[col]) for row in table) for col in range(numCols)] # column widths

        # --- apply column widths with alignments ---
        if hasHeader: # header is centered
            for x in range(numCols): table[0][x] = table[0][x].center(widths[x])
        for y in range(hasHeader,numRows): # apply column alignments
            for x in range(numCols): c = table[y][x]; table[y][x] = [c.ljust,c.rjust,c.center][align[x]](widths[x])

        # --- data for printing
        P = " "*pad; LSEP,SEP,RSEP = "│"+P, P+"│"+P, P+"│"
        lines = ["─"*(widths[col]+pad*2) for col in range(numCols)]

        drawLine = [isGrid]*numRows; drawLine[0]|=hasHeader; drawLine[-1] = False
        if hasHeader or isGrid: gridLine = "├"+"┼".join(lines)+"┤" # if any(drawLine)

        # --- print rows ---
        print("┌"+"┬".join(lines)+"┐")
        for y in range(numRows):
            print(LSEP+SEP.join(table[y])+RSEP)
            if drawLine[y]: print(gridLine)
        print("└"+"┴".join(lines)+"┘")