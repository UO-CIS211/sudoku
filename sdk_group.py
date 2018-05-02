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
        """A group is consistent if it has no duplicates,
        every tile has at least one candidate, and
        every possible value can be placed somewhere in the group.
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
            if tile.value == sdk_tile.UNKNOWN:
                continue
            elif tile.value in used:
                reports.append("Duplicate in {}: {}, value {}"
                               .format(self.title, self, tile.value))
        return reports

    # ---------------------------------
    # Constraint propagation in a group
    # ----------------------------------

    def naked_single_constrain(self) -> bool:
        """A choice can be used at most once in the group.
        For each choice that has already been used in the group,
        eliminate that choice as a candidate in all the
        UNKNOWN tiles in the group.
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
        """Each choice must be used in the group.
        For each choice that has not already been used
        in the group, if there is exactly one tile in the
        group for which it is a candidate, then that
        tile must hold that choice.
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

            possible_tile = possible_tiles[0]
            only_one_possible = len(possible_tiles) == 1
            tile_is_unknown = possible_tile.value == sdk_tile.UNKNOWN

            # If there is only one possible tile AND that tiles value is UNKNOWN
            # Then that tile must have that value
            if only_one_possible and tile_is_unknown:
                all_but_val = set(sdk_tile.CHOICES) - {val}
                possible_tile.eliminate(all_but_val)
                changed = True

        self.unattend()
        return changed
