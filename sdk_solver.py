"""
Sudoku solution tactics.  These include the
constraint propogation tactics and (in phase
two) the search-based solver.

Author: FIXME
"""

from sdk_board import Board
import sdk_tile

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def naked_single(board: Board) -> bool:
    """As described in http://www.sadmansoftware.com/sudoku/nakedsingle.php
    Returns True iff some change has been made
    """
    logging.info("Applying naked single tactic")
    changed = False
    for group in board.groups:
        changed = group.naked_single_constrain() or changed
    return changed


def hidden_single(board: Board) -> bool:
    """As described in http://www.sadmansoftware.com/sudoku/hiddensingle.php
    Returns True iff some change has been made
    """
    logging.info("Applying hidden single tactic")
    changed = False
    for group in board.groups:
        changed = group.hidden_single_constrain() or changed
    return changed


def propagate(board: Board):
    """Propagate constraints until we either solve the puzzle,
    show the puzzle as given is unsolvable, or can make no more
    progress by constraint propagation.
    """
    logging.info("Propagating constraints")
    changed = True
    while changed:
        logging.info("Invoking naked single")
        changed = naked_single(board)
        if board.is_solved() or not board.is_consistent():
            return
        changed = hidden_single(board) or changed
        if board.is_solved() or not board.is_consistent():
            return
    return


def solve(board: Board) -> bool:
    """Main solver.  Initially this just invokes constraint
    propagation.  In part 2 of the project, you will add
    recursive back-tracking search (guess-and-check with recursion).
    A complete solution for solve for part 2 will
    - find the the best tile to guess values for
    - guess each possible value for that tile
    - if a guess is wrong, reset the board
    - return True if the board is solved, false otherwise
    """
    log.debug("Called solve on board:\n{}".format(board))
    propagate(board)
    if board.is_solved():
        return True
    if not board.is_consistent():
        return False

    log.info("Invoking back-track search")
    # There must be at least one tile with value UNKNOWN
    # and multiple candidate values.  Choose one with
    # fewest candidates.
    min_candidates = len(sdk_tile.CHOICES) + 1
    best_tile = None
    for row in board.tiles:
        for tile in row:
            if (tile.value == sdk_tile.UNKNOWN) and (len(tile.candidates) < min_candidates):
                min_candidates = len(tile.candidates)
                best_tile = tile

    assert not (best_tile is None)  # best_tile should never be None. If it is, we've made a mistake

    log.info("Guess-and-check on tile[{}][{}]".format(best_tile.row, best_tile.col))
    saved = board.as_list()
    for guess in best_tile.candidates:
        best_tile.set_value(guess)
        log.info("Guessing {}".format(guess))
        if solve(board):
            return True

        # That guess didn't work. Restore old board and try again
        board.set_tiles(saved)

    return False

