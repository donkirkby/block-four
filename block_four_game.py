from collections import namedtuple, Counter

from mittmcts import Draw

BlockFourState = namedtuple('BlockFourState',
                            ['cells',  # [[None, 1, -1]] 9x9
                             'player'])  # next player to move: -1 or 1


BlockFourMove = namedtuple('BlockFourMove', 'row column')  # values 0-8


class BlockFourGame:
    """ Creates game states and moves. """
    def __init__(self, field_size=3, field_count=3):
        self.field_size = field_size
        self.field_count = field_count

    def initial_state(self, player=1, cells: str=None):
        grid_size = self.field_size * self.field_count
        new_cells = [[None] * grid_size for _ in range(grid_size)]
        if cells is not None:
            for i, row in enumerate(cells.splitlines(keepends=False)):
                for j, cell in enumerate(row):
                    if cell == '+':
                        new_cells[i][j] = 1
                    elif cell == '-':
                        new_cells[i][j] = -1
        return BlockFourState(cells=new_cells,
                              player=player)

    @staticmethod
    def format(state):
        return '\n'.join(''.join('+' if cell == 1
                                 else '-' if cell == -1
                                 else '.'
                                 for cell in row)
                         for row in state.cells)

    def apply_move(self, state: BlockFourState, move: BlockFourMove):
        new_cells = [row[:] for row in state.cells]
        player = state.player
        new_cells[move.row][move.column] = player
        rows_field = move.row // self.field_size
        columns_field = move.column // self.field_size
        start_row = rows_field * self.field_size
        stop_row = start_row + self.field_size
        start_column = columns_field * self.field_size
        stop_column = start_column + self.field_size
        counter = Counter(new_cells[row][column]
                          for row in range(start_row, stop_row)
                          for column in range(start_column, stop_column))
        top_player, count = counter.most_common(1)[0]
        if count * 2 > self.field_size * self.field_size:
            for row in range(start_row, stop_row):
                for column in range(start_column, stop_column):
                    if new_cells[row][column] is None:
                        new_cells[row][column] = top_player

        player = -player
        return BlockFourState(new_cells, player)

    @staticmethod
    def get_winner(state: BlockFourState):
        try:
            total = sum(cell for row in state.cells for cell in row)
        except TypeError:
            return None

        return 1 if total > 0 else -1 if total < 0 else Draw

    @staticmethod
    def current_player(state: BlockFourState):
        return state.player

    @staticmethod
    def get_moves(state: BlockFourState):
        return False, [BlockFourMove(i, j)
                       for i, row in enumerate(state.cells)
                       for j, cell in enumerate(row)
                       if cell is None]
