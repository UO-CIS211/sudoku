"""
A "group" is a collection of 9 Sudoku tiles, which
may form a row, a column, or a block (aka 'region'
or 'box').

Constraint propagation are localized here.
"""

from typing import Sequence, List

import sdk_tile

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.WARN)


class Group(object):
    """A group of 9 Sudoku tiles"""

    def __init__(self, title: str):
        """Initially empty.  The title is just for debugging."""
        self.title = title
        self.tiles: List[sdk_tile.Tile] = []

    def add(self, tile: sdk_tile.Tile):
        """Add a tile to this group"""
        assert len(self.tiles) < 9
        self.tiles.append(tile)

    def __str__(self):
        """Represent as string of values"""
        values = []
        for tile in self.tiles:
            values.append(tile.value)
        return self.title + " " + "".join(values)

    def attend(self):
        """Announce that we are working on these tiles.  A view component
        may make this visible.
        """
        for tile in self.tiles:
            tile.attend()

    def unattend(self):
        """Announce that we are done working on these tiles for now"""
        for tile in self.tiles:
            tile.unattend()

    def is_complete(self) -> bool:
        """A group is complete if all of its tiles hold a
        value (not the wild-card symbol UNKNOWN)
        """
        for tile in self.tiles:
            if tile.value == sdk_tile.UNKNOWN:
                return False
        return True

    def is_consistent(self) -> bool:
        """
        A complete solution for is_consistent will return False if:
        - a group has two or more tiles with the same value,
        - any tile does not have at least one possible value
        - any value in CHOICES can not be placed somewhere in the group.
        return True otherwise
        """

        can_place = set()
        used = set()
        for tile in self.tiles:
            # At least one candidate?
            if len(tile.candidates) == 0:
                # No place to go!
                return False
            if tile.value in used:
                # Duplicate!
                return False
            elif tile.value != sdk_tile.UNKNOWN:
                used.add(tile.value)
            # A place for every tile?
            can_place = can_place.union(tile.candidates)

        # every value has a place to go
        return can_place == set(sdk_tile.CHOICES)

    def duplicates(self) -> Sequence[str]:
        """One line report per duplicate found"""
        reports = []
        used = set()
        for tile in self.tiles:
            if tile.value in used:
                reports.append("Duplicate in {}: {}, value {}"
                               .format(self.title, self, tile.value))
            if tile.value in sdk_tile.CHOICES:
                used.add(tile.value)

        return reports

    # ---------------------------------
    # Constraint propagation in a group
    # ----------------------------------

    def naked_single_constrain(self) -> bool:
        """
        A choice may only exist once in a group
        A complete solution to naked_single_constrain will:
        - find all values in the group that are already set
        - remove those values as possibilities from the unset tiles in the group
        - return True if a change has been made, False otherwise
        """

        # Which values have already been used?
        #  If any tile in the group has value X,
        #  then value X can't be a candidate for any unknown
        #  tile in the group

        self.attend()
        changed = False
        used = set()

        # Find the value of all tiles that are decided
        for tile in self.tiles:
            if tile.value != sdk_tile.UNKNOWN:
                used.add(tile.value)

        # Already used values can't be used twice,
        # remove them from the unknown tiles
        for tile in self.tiles:
            if tile.value == sdk_tile.UNKNOWN:
                changed = tile.eliminate(used) or changed

        self.unattend()
        return changed

    def hidden_single_constrain(self) -> bool:
        """
        Each choice must be possible in a group.
        A complete solution for hidden_single_constrain will
        - for each possible choice, if that choice can only
          exist in one tile in the group and that tile is not
          already set, set the tile to be that choice
        - return True if any tile was set, False otherwise
        """
        self.attend()
        changed = False

        # Each value must go somewhere
        for val in sdk_tile.CHOICES:
            possible_tiles = []
            # Find all the tiles that this val could assigned to
            for tile in self.tiles:
                if val in tile.candidates:
                    possible_tiles.append(tile)

            only_one_possible = len(possible_tiles) == 1
            tile_is_unknown = False
            if only_one_possible:
                tile_is_unknown = possible_tiles[0].value == sdk_tile.UNKNOWN

            # If there is only one possible tile AND that tiles value is UNKNOWN
            # Then that tile must have that value
            if only_one_possible and tile_is_unknown:
                all_but_val = set(sdk_tile.CHOICES) - {val}
                possible_tiles[0].eliminate(all_but_val)
                changed = True

        self.unattend()
        return changed
