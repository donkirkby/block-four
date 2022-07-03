from collections import namedtuple
from logging import basicConfig, getLogger, WARN
from queue import Queue, Empty
from threading import Thread

import mittmcts
import pygame

from block_four_game import BlockFourGame, BlockFourMove

basicConfig(format='%(asctime)s %(message)s', level=WARN)
logger = getLogger(__name__)

BLACK = 100, 100, 100
RED = 200, 0, 0
GREEN = 0, 200, 0
WHITE = 255, 255, 255
DIRECTIONS = {pygame.K_w: [0, -1],
              pygame.K_s: [0, 1],
              pygame.K_a: [-1, 0],
              pygame.K_d: [1, 0]}


WindowSize = namedtuple('WindowSize', 'grid_size line_width grid_x grid_y')


class Game:
    def __init__(self, surface=None, opponent_iterations=10):
        pygame.init()
        pygame.mixer.quit()  # Avoids high CPU.

        self.speed = [2, 2]
        self.row_length = 9

        self.background = (100, 100, 100)
        self.grid_colour = (20, 20, 20)
        self.player_colour = (100, 100, 250)
        self.opponent_colour = (100, 200, 100)

        if surface is not None:
            self.surface = surface
            self.width, self.height = surface.get_size()
        else:
            icon = create_icon(self.opponent_colour, self.player_colour)
            pygame.display.set_icon(icon)
            self.width, self.height = 320, 240
            self.surface = pygame.display.set_mode((self.width, self.height),
                                                   pygame.RESIZABLE)

        self.size = self.rescale()
        self.piece_shapes = (('**',
                              '**'),
                             ('**',
                              ' **'),
                             ('***',
                              ' *'),
                             ('***',
                              '*'),
                             ('****',
                              ''))
        self.game = BlockFourGame()
        self.state = self.game.initial_state()
        self.winner = self.game.get_winner(self.state)
        self.state_queue = Queue()
        self.opponent_result_queue = Queue()
        opponent_thread = Thread(target=run_opponent,
                                 args=(self.game,
                                       self.state_queue,
                                       self.opponent_result_queue,
                                       opponent_iterations),
                                 daemon=True)
        opponent_thread.start()

    def rescale(self):
        grid_size = min(self.width, self.height) * .5
        return WindowSize(grid_size=grid_size,
                          line_width=self.width // 300,
                          grid_x=(self.width - grid_size) * .5,
                          grid_y=(self.height - grid_size) * .5)

    def draw_grid_line(self, x1, y1, x2, y2):
        colour = (self.player_colour if self.winner == 1
                  else self.opponent_colour if self.winner == -1
                  else self.grid_colour)
        self.surface.fill(colour,
                          (x1, y1, x2-x1, y2-y1))

    def draw(self, markers='  '):
        self.surface.fill(self.background)
        outer_x1 = self.size.grid_x - self.size.line_width
        inner_x1 = outer_x1 + 2*self.size.line_width
        inner_x2 = outer_x1 + self.size.grid_size
        outer_x2 = inner_x2 + 2*self.size.line_width
        outer_y1 = self.size.grid_y - self.size.line_width
        inner_y1 = outer_y1 + 2*self.size.line_width
        inner_y2 = outer_y1 + self.size.grid_size
        outer_y2 = inner_y2 + 2*self.size.line_width
        for i in range(8):
            y = self.size.grid_y + (i + 1) * self.size.grid_size / self.row_length
            line_width = (self.size.line_width*2
                          if (i % 3) == 2
                          else self.size.line_width)
            pygame.draw.line(self.surface,
                             self.grid_colour,
                             (self.size.grid_x,
                              y),
                             ((self.width + self.size.grid_size) * .5,
                              y),
                             line_width)
            x = self.size.grid_x + (i + 1) * self.size.grid_size / self.row_length
            pygame.draw.line(self.surface,
                             self.grid_colour,
                             (x,
                              self.size.grid_y),
                             (x,
                              (self.height + self.size.grid_size) * .5),
                             line_width)
        self.draw_grid_line(outer_x1, outer_y1, outer_x2, inner_y1)
        self.draw_grid_line(outer_x1, inner_y2, outer_x2, outer_y2)
        self.draw_grid_line(outer_x1, inner_y1, inner_x1, outer_y2)
        self.draw_grid_line(inner_x2, inner_y1, outer_x2, outer_y2)

        self.draw_pieces(outer_x2,
                         outer_y1,
                         self.opponent_colour,
                         dir=-1,
                         marker=markers[0])
        self.draw_pieces(outer_x1,
                         outer_y2,
                         self.player_colour,
                         dir=1,
                         marker=markers[1])
        self.draw_spaces()

    def draw_pieces(self, start_x, start_y, colour, dir, marker=''):
        step_size = self.size.grid_size / self.row_length
        x = start_x + dir * (self.size.line_width - 5*step_size)
        y = start_y
        for shape in self.piece_shapes:
            y = start_y
            if dir < 0:
                y -= 3*step_size
            else:
                y += step_size
            for j, row in enumerate(shape):
                for i, cell in enumerate(row):
                    if cell != ' ':
                        self.surface.fill(colour,
                                          (x + dir*i*step_size,
                                           y + j*step_size,
                                           step_size+1,
                                           step_size+1))
            x += dir * step_size * (1 + max(len(row) for row in shape))
        font = pygame.font.SysFont('monospace', 22)
        label = font.render(marker, 1, colour)
        self.surface.blit(label, (x, y))

    def draw_spaces(self):
        step_size = self.size.grid_size / self.row_length
        radius = round(self.size.grid_size / 22)
        for row in range(self.row_length):
            for column in range(self.row_length):
                player = self.game.get_cell(self.state, row, column)
                if player:
                    x = round(self.size.grid_x + (column + 0.5)*step_size)
                    y = round(self.size.grid_y + (row + 0.5)*step_size)
                    colour = (self.player_colour
                              if player == 1
                              else self.opponent_colour)
                    pygame.draw.circle(self.surface,
                                       colour,
                                       (x, y),
                                       radius)

    def draw_polygon(self, colour, start_pos, step_size, *steps):
        pos = start_pos
        points = [start_pos]
        for step in steps:
            pos = (pos[0] + step[0]*step_size, pos[1] + step[1]*step_size)
            points.append(pos)
        pygame.draw.polygon(self.surface,
                            colour,
                            points)

    def click(self, pos):
        if self.winner or self.state.player != 1:
            return
        x, y = pos
        step_size = self.size.grid_size / self.row_length
        row = int((y - self.size.grid_y) // step_size)
        column = int((x - self.size.grid_x) // step_size)
        if row < 0 or self.row_length <= row:
            return
        if column < 0 or self.row_length <= column:
            return
        self.state = self.game.apply_move(self.state, BlockFourMove(row, column))
        self.winner = self.game.get_winner(self.state)
        if self.winner:
            return
        self.state_queue.put(self.state)

    def main_loop(self):
        self.draw()
        pygame.display.flip()
        if self.state.player == -1:
            self.state_queue.put(self.state)
        while True:
            event = pygame.event.poll()
            if event.type != pygame.NOEVENT:
                logger.debug('received event %s', event)
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.surface = pygame.display.set_mode((self.width, self.height),
                                                       pygame.RESIZABLE)
                self.size = self.rescale()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.click(event.pos)
            elif event.type == pygame.NOEVENT:
                try:
                    result = self.opponent_result_queue.get(timeout=0.1)
                except Empty:
                    continue
                self.state = self.game.apply_move(self.state, result.move)
                self.winner = self.game.get_winner(self.state)
            else:
                continue
            self.draw()
            pygame.display.flip()


def run_opponent(game: BlockFourGame,
                 state_queue: Queue,
                 result_queue: Queue,
                 opponent_iterations: int):
    logger.info('Starting opponent.')
    while True:
        state = state_queue.get()
        logger.debug('received state')
        searcher = mittmcts.MCTS(game, state)
        result = searcher.get_simulation_result(opponent_iterations)
        logger.debug('sending result')
        result_queue.put(result)


def create_icon(colour1, colour2):
    surface = pygame.Surface((128, 128))
    background = (100, 100, 100)
    surface.fill(background)
    pygame.draw.polygon(surface,
                        colour1,
                        ((4, 4),
                         (4, 84),
                         (44, 84),
                         (44, 44),
                         (124, 44),
                         (124, 4)))
    pygame.draw.polygon(surface,
                        colour2,
                        ((124, 124),
                         (124, 44),
                         (84, 44),
                         (84, 84),
                         (4, 84),
                         (4, 124)))
    return surface


def live_main():
    surface = pygame.Surface((300, 200))
    try:
        game = Game(surface)
        game.background = (250, 250, 250)
        game.player_colour = (200, 0, 0)
        game.opponent_colour = (0, 0, 0)
        game.state = game.game.initial_state(cells="""\
""")
        click_pos = (172, 112)
        # game.click(click_pos)
        game.draw(markers='XO')
        # pygame.draw.circle(surface, game.opponent_colour, click_pos, 2)
    except Exception as ex:
        surface.fill(BLACK)
        print(ex)
    pygame.image.save(surface, 'live.png')


def main():
    game = Game(opponent_iterations=1000)
    game.main_loop()


if __name__ == '__main__':
    main()
elif __name__ == '__live_coding__':
    live_main()
