"""
A Sudoku board holds a 9x9 matrix of tiles.
Each row and column and also 9 3x3 sub-blocks
are treated as a group of 9 (sometimes called
a 'nonet'); when solved, each group must contain
exactly one occurence of each of the 9 symbols
on the board.
"""

from typing import Sequence, List

from events import Event, Listener
from sdk_tile import Tile, UNKNOWN
from sdk_group import Group

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.WARN)


# -------------------------------
# Interface for listeners
# -------------------------------


class BoardEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self):
        pass


class BoardListener(Listener):
    def notify(self, event: BoardEvent):
        raise NotImplementedError(
            "BoardListener subclass needs to override notify(BoardEvent)")

# ------------------------------
#  Board class
# ------------------------------


class Board(object):
    """A board has a matrix of tiles indexed 0..9, 0..9"""

    def __init__(self):
        """The empty board"""
        # Row/Column structure: Each row contains columns
        self.tiles: List[List[Tile]] = []
        for row in range(9):
            cols = []
            for col in range(9):
                cols.append(Tile(row, col))
            self.tiles.append(cols)

        self.groups = []
        self._form_groups()

    def _form_groups(self):
        """Build a group for each row, column, and block """
        self._build_row_groups()
        self._build_column_groups()
        self._build_block_groups()

    def _build_row_groups(self):
        """Add a group for each row"""
        for row_index in range(9):
            row_group = Group("Row {}".format(row_index + 1))
            for col_index in range(9):
                row_group.add(self.tiles[row_index][col_index])
            self.groups.append(row_group)

    def _build_column_groups(self):
        """Add a group for each column"""
        for col_index in range(9):
            col_group = Group("Column {}".format(col_index))
            for row_index in range(9):
                col_group.add(self.tiles[row_index][col_index])
            self.groups.append(col_group)

    def _build_block_groups(self):
        """Add a group for each 3x3 block"""
        for row_group in range(3):
            for col_group in range(3):
                block_group = Group("Block from {},{}"
                                    .format(row_group, col_group))
                row_base = 3 * row_group
                col_base = 3 * col_group
                for row_offset in range(3):
                    for col_offset in range(3):
                        tile_row = row_base + row_offset
                        tile_col = col_base + col_offset
                        block_group.add(self.tiles[tile_row][tile_col])
                self.groups.append(block_group)

    def set_tiles(self, tile_values: Sequence[Sequence[str]]):
        """Set the tile values a list of lists or a list of strings"""
        for row_num in range(9):
            for col_num in range(9):
                tile = self.tiles[row_num][col_num]
                tile.set_value(tile_values[row_num][col_num])

    def as_list(self) -> List[str]:
        """Get tile values in a format for printing or for
        saving and later restoring with set_tiles
        """
        rep = []
        for row in self.tiles:
            row_rep = []
            for tile in row:
                row_rep.append(str(tile))
            rep.append("".join(row_rep))
        return rep

    def is_consistent(self) -> bool:
        """All the constraints are satisfied, so far"""
        for group in self.groups:
            if not group.is_consistent():
                log.debug("Inconsistent group {}".format(group))
                return False
        return True

    def duplicates(self) -> Sequence[str]:
        """A list of duplicates found in groups"""
        reports = []
        for group in self.groups:
            reports = reports + group.duplicates()
        return reports

    def is_solved(self) -> bool:
        """Are we there yet?"""
        if not self.is_consistent():
            return False
        for row in self.tiles:
            for tile in row:
                if tile.value == UNKNOWN:
                    return False
        return True

    def __str__(self) -> str:
        return "\n".join(self.as_list())
