from collections import namedtuple
from random import choice

from mittmcts import Draw

BlockFourState = namedtuple('BlockFourState',
                            ['pos_cells',  # integer of bit flags
                             'neg_cells',  # integer of bit flags
                             'player'])  # next player to move: -1 or 1


BlockFourMove = namedtuple('BlockFourMove', 'row column')  # values 0-8


class BlockFourGame:
    """ Creates game states and moves. """
    def __init__(self, field_size=3, field_count=3):
        self.field_size = field_size
        self.field_count = field_count

    def initial_state(self, player=None, cells: str=None):
        if player is None:
            player = choice((1, -1))
        grid_size = self.field_size * self.field_count
        pos_cells = 0
        neg_cells = 0
        if cells is not None:
            for i, row in enumerate(cells.splitlines(keepends=False)):
                for j, cell in enumerate(row):
                    bit = 1 << grid_size*i + j
                    if cell == '+':
                        pos_cells |= bit
                    elif cell == '-':
                        neg_cells |= bit
        return BlockFourState(pos_cells=pos_cells,
                              neg_cells=neg_cells,
                              player=player)

    def format(self, state):
        size = self.get_size()
        rows = ((self.get_cell(state, row, column)
                 for column in range(size))
                for row in range(size))
        return '\n'.join(''.join('+' if cell == 1
                                 else '-' if cell == -1
                                 else '.'
                                 for cell in row)
                         for row in rows)

    def get_cell(self, state: BlockFourState, row, column):
        bit = 1 << self.get_size()*row + column
        return (1 if state.pos_cells & bit
                else -1 if state.neg_cells & bit
                else None)

    def get_size(self):
        return self.field_size * self.field_count

    def apply_move(self, state: BlockFourState, move: BlockFourMove):
        player = state.player
        active_cells, other_cells = ((state.pos_cells, state.neg_cells)
                                     if player == 1
                                     else (state.neg_cells, state.pos_cells))

        grid_size = self.get_size()
        bit = 1 << (move.row * grid_size + move.column)
        active_cells |= bit
        rows_field = move.row // self.field_size
        columns_field = move.column // self.field_size
        start_row = rows_field * self.field_size
        stop_row = start_row + self.field_size
        start_column = columns_field * self.field_size
        stop_column = start_column + self.field_size
        bit_count = sum(0 != (active_cells & 1 << (row * grid_size + column))
                        for row in range(start_row, stop_row)
                        for column in range(start_column, stop_column))
        if bit_count * 2 > self.field_size * self.field_size:
            for row in range(start_row, stop_row):
                for column in range(start_column, stop_column):
                    bit = 1 << (row * grid_size + column)
                    if bit & other_cells == 0:
                        active_cells |= bit

        pos_cells, neg_cells = ((active_cells, other_cells)
                                if player == 1
                                else (other_cells, active_cells))
        player = -player
        return BlockFourState(pos_cells, neg_cells, player)

    def get_winner(self, state: BlockFourState):
        grid_size = self.get_size()
        max_count = grid_size * grid_size
        pos_count = bin(state.pos_cells).count("1")
        neg_count = bin(state.neg_cells).count("1")
        if pos_count + neg_count < max_count:
            return None
        if pos_count > neg_count:
            return 1
        if pos_count < neg_count:
            return -1
        return Draw

    @staticmethod
    def current_player(state: BlockFourState):
        return state.player

    def get_field_moves(self, state: BlockFourState, row_field, column_field):
        start_row = row_field * self.field_size
        for row in range(start_row, start_row + self.field_size):
            start_column = column_field * self.field_size
            for column in range(start_column,
                                start_column + self.field_size):
                if self.get_cell(state, row, column) is None:
                    yield BlockFourMove(row, column)
                    return

    def get_moves(self, state: BlockFourState):
        moves = []
        for row_field in range(self.field_count):
            for column_field in range(self.field_count):
                moves.extend(self.get_field_moves(state, row_field, column_field))
        return False, moves
