""" I use this to watch an image for changes while doing live coding.

If I tell the window to always stay on top, I can see it while I edit my code
in live coding mode.
"""

from argparse import ArgumentParser, FileType
from pathlib import Path

import pygame


def parse_args():
    parser = ArgumentParser(description='Displays a changing image file.')
    parser.add_argument('image', type=Path)
    return parser.parse_args()


def main():
    size = 50, 50
    args = parse_args()
    pygame.init()
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
