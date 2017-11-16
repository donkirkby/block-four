from itertools import accumulate

import pygame

BLACK = 100, 100, 100
RED = 200, 0, 0
GREEN = 0, 200, 0
WHITE = 255, 255, 255
DIRECTIONS = {pygame.K_w: [0, -1],
              pygame.K_s: [0, 1],
              pygame.K_a: [-1, 0],
              pygame.K_d: [1, 0]}


class Game:
    def __init__(self, surface=None):
        pygame.init()
        pygame.mixer.quit()

        self.speed = [2, 2]

        if surface is not None:
            self.surface = surface
            self.width, self.height = surface.get_size()
        else:
            self.width, self.height = 320, 240
            self.surface = pygame.display.set_mode((self.width, self.height),
                                                   pygame.RESIZABLE)
        self.background = (100, 100, 100)
        self.grid_colour = (20, 20, 20)
        self.player_colour = (100, 100, 250)
        self.opponent_colour = (100, 200, 100)
        self.grid_size, self.line_width = self.rescale()
        self.piece_shapes = (('**',
                              '**'),
                             ('***',
                              '*'),
                             ('***',
                              ' *'),
                             ('**',
                              ' **'),
                             ('****',
                              ''))

    def rescale(self):
        return min(self.width, self.height) * .5, self.width // 300

    def draw_grid_line(self, x1, y1, x2, y2):
        self.surface.fill(self.grid_colour,
                          (x1, y1, x2-x1, y2-y1))

    def draw(self):
        self.surface.fill(self.background)
        outer_x1 = (self.width - self.grid_size) * .5 - self.line_width
        inner_x1 = outer_x1 + 2*self.line_width
        inner_x2 = outer_x1 + self.grid_size
        outer_x2 = inner_x2 + 2*self.line_width
        outer_y1 = (self.height - self.grid_size) * .5 - self.line_width
        inner_y1 = outer_y1 + 2*self.line_width
        inner_y2 = outer_y1 + self.grid_size
        outer_y2 = inner_y2 + 2*self.line_width
        self.draw_grid_line(outer_x1, outer_y1, outer_x2, inner_y1)
        self.draw_grid_line(outer_x1, inner_y2, outer_x2, outer_y2)
        self.draw_grid_line(outer_x1, inner_y1, inner_x1, outer_y2)
        self.draw_grid_line(inner_x2, inner_y1, outer_x2, outer_y2)
        for i in range(8):
            y = (self.height - self.grid_size) * .5 + (i + 1) * self.grid_size / 9
            line_width = self.line_width*2 if (i % 3) == 2 else self.line_width
            pygame.draw.line(self.surface,
                             self.grid_colour,
                             ((self.width - self.grid_size) * .5,
                              y),
                             ((self.width + self.grid_size) * .5,
                              y),
                             line_width)
            x = (self.width - self.grid_size) * .5 + (i + 1) * self.grid_size / 9
            pygame.draw.line(self.surface,
                             self.grid_colour,
                             (x,
                              (self.height - self.grid_size) * .5),
                             (x,
                              (self.height + self.grid_size) * .5),
                             line_width)

        self.draw_pieces2(outer_x1, outer_y2, self.player_colour, ydir=1)
        self.draw_pieces2(outer_x1, outer_y1, self.opponent_colour, ydir=-1)

    def draw_pieces2(self, start_x, start_y, colour, ydir):
        step_size = self.grid_size / 9
        x = start_x + self.line_width - 5*step_size
        for shape in self.piece_shapes:
            y = start_y
            if ydir < 0:
                y -= 3*step_size
            else:
                y += step_size
            for j, row in enumerate(shape):
                for i, cell in enumerate(row):
                    if cell != ' ':
                        self.surface.fill(colour,
                                          (x + i*step_size,
                                           y + j*step_size,
                                           step_size+1,
                                           step_size+1))
            x += step_size * (1 + max(len(row) for row in shape))

    def draw_pieces(self, start_x, start_y, colour, ydir):
        step_size = self.grid_size / 9
        x = start_x + self.line_width - 5*step_size
        self.draw_polygon(colour,
                          (x, start_y + ydir*self.grid_size / 9),
                          step_size,
                          (0, 2*ydir),
                          (2, 0),
                          (0, -2*ydir))
        x += 3*step_size
        self.draw_polygon(colour,
                          (x, start_y + ydir*self.grid_size / 9),
                          step_size,
                          (0, ydir),
                          (1, 0),
                          (0, ydir),
                          (1, 0),
                          (0, -ydir),
                          (1, 0),
                          (0, -ydir))
        x += 4*step_size
        self.draw_polygon(colour,
                          (x, start_y + ydir*self.grid_size / 9),
                          step_size,
                          (0, ydir),
                          (1, 0),
                          (0, ydir),
                          (2, 0),
                          (0, -ydir),
                          (-1, 0),
                          (0, -ydir))
        x += 4*step_size
        self.draw_polygon(colour,
                          (x, start_y + ydir*self.grid_size / 9),
                          step_size,
                          (0, ydir),
                          (2, 0),
                          (0, ydir),
                          (1, 0),
                          (0, -2*ydir))
        x += 4*step_size
        self.draw_polygon(colour,
                          (x, start_y + ydir*self.grid_size / 9),
                          step_size,
                          (0, ydir),
                          (4, 0),
                          (0, -ydir))

    def draw_polygon(self, colour, start_pos, step_size, *steps):
        pos = start_pos
        points = [start_pos]
        for step in steps:
            pos = (pos[0] + step[0]*step_size, pos[1] + step[1]*step_size)
            points.append(pos)
        pygame.draw.polygon(self.surface,
                            colour,
                            points)

    def main_loop(self):
        self.draw()
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    pygame.time.wait(100)
                    self.surface = pygame.display.set_mode((self.width, self.height),
                                                           pygame.RESIZABLE)
                    self.grid_size, self.line_width = self.rescale()
                    pygame.display.update()
                    self.draw()
                    pygame.display.flip()
            pygame.time.wait(500)


def live_main():
    surface = pygame.Surface((300, 200))
    try:
        game = Game(surface)
        game.draw()
    except Exception as ex:
        surface.fill(BLACK)
        print(ex)
    pygame.image.save(surface, 'live.png')


def main():
    game = Game()
    game.main_loop()


if __name__ == '__main__':
    main()
elif __name__ == '__live_coding__':
    live_main()
