""" I use this to watch an image for changes while doing live coding.

If I tell the window to always stay on top, I can see it while I edit my code
in live coding mode.
"""

from argparse import ArgumentParser
from pathlib import Path

import pygame


def parse_args():
    parser = ArgumentParser(description='Displays a changing image file.')
    parser.add_argument('image', type=Path)
    return parser.parse_args()


def create_icon():
    handle = pygame.Surface((18, 90))
    surface = pygame.Surface((128, 128))
    background = (100, 100, 100)
    foreground = (0, 0, 0)
    handle.fill(background)
    handle.fill(foreground, (3, 0, 12, 100))
    handle = pygame.transform.rotate(handle, 45)
    surface.fill(background)
    size = 40
    surface.blit(handle, (size+5, size+5))
    pygame.draw.circle(surface, foreground, (size + 5, size + 5), size)
    pygame.draw.circle(surface, background, (size + 5, size + 5), size - 10)
    return surface


def main():
    size = 50, 50
    args = parse_args()
    pygame.init()
    pygame.mixer.quit()  # Avoids high CPU.
    pygame.display.set_icon(create_icon())
    timestamp = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        new_timestamp = args.image.stat().st_mtime
        if new_timestamp != timestamp:
            try:
                # noinspection PyUnresolvedReferences
                image = pygame.image.load(str(args.image))
                size = image.get_rect().size
                surface = pygame.display.set_mode(size)
                surface.blit(image, image.get_rect())
                timestamp = new_timestamp
            except pygame.error:
                surface = pygame.display.set_mode(size)
                surface.fill((0, 0, 0))
            pygame.display.flip()
        pygame.time.wait(100)


main()
