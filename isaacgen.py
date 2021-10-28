import argparse
import os
import random

from contextlib import redirect_stdout
from pathlib import Path

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

CELLW, CELLH = (50, 44)
WIDTH, HEIGHT = SIZE = (800, 500)

class Images:
    """
    Dict-like with attribute access, set item as path, get item as pygame.Surface.
    """

    def __init__(self):
        self._images = {}

    def __setitem__(self, key, path):
        if key in self._images:
            raise KeyError(f'{key} already set.')
        self._images[key] = path

    def __getitem__(self, key):
        path = self._images[key]
        if isinstance(path, (str, Path)):
            self._images[key] = pygame.image.load(path)
        return self._images[key]

    def __setattr__(self, key, path):
        if key != '_images':
            self[key] = path
        else:
            super().__setattr__(key, path)

    def __getattr__(self, key):
        return self[key]


class IsaacGenerator:

    def __init__(self, tilesheet, minrooms=7, maxrooms=15):
        self.tilesheet = tilesheet
        self.minrooms = minrooms
        self.maxrooms = maxrooms

    def start(self):
        self.boss = None
        self.cellqueue = []
        self.endrooms = []
        self.floorplan = [0 for _ in range(101)]
        self.placed_special = False
        self.sprites = []
        self.started = False
        self.started = True
        self.visit(45)

    def visit(self, index):
        if self.floorplan[index]:
            return False

        neighbors = self.ncount(index)
        if neighbors > 1:
            return False

        if sum(self.floorplan) >= self.maxrooms:
            return False

        if index != 45 and random.choice([True, False]):
            return False

        self.cellqueue.append(index)
        self.floorplan[index] = 1

        self.add_image(index, 'cell')
        return True

    def add_image(self, index, name):
        x = index % 10
        y = (index - x) / 10
        _x = WIDTH / 2 + CELLW * (x - 5)
        _y = HEIGHT / 2 + CELLH * (y - 4)
        image = self.tilesheet[name]
        sprite = (image, (_x, _y))
        self.sprites.append(sprite)
        return image

    def ncount(self, index):
        populated_neighbors = sum([
            self.floorplan[index - 10],
            self.floorplan[index - 1],
            self.floorplan[index + 1],
            self.floorplan[index + 10],
        ])
        return populated_neighbors

    def update(self):
        if not self.started:
            return
        if len(self.cellqueue) > 0:
            self._update_cellqueue()
        elif not self.placed_special:
            self._update_finish_or_restart()

    def _update_cellqueue(self):
        index = self.cellqueue.pop(0)
        x = index % 10
        created = False
        if x > 1:
            created = created or self.visit(index - 1)
        if x < 9:
            created = created or self.visit(index + 1)
        if index > 20:
            created = created or self.visit(index - 10)
        if index < 70:
            created = created or self.visit(index + 10)
        if not created:
            self.endrooms.append(index)

    def _update_finish_or_restart(self):
        if sum(self.floorplan) < self.minrooms:
            # start / restart
            self.start()
            return
        # boss
        self.placed_special = True
        self.boss = self.endrooms.pop()
        image = self.tilesheet.boss
        try:
            # reward
            reward_index = self.poprandomendroom()
            image = self.tilesheet.reward
            self.add_image(reward_index, 'reward')
            # coin
            coin_index = self.poprandomendroom()
            self.add_image(coin_index, 'coin')
            secret_index = self.picksecretroom()
            # cell and secret
            self.add_image(secret_index, 'cell')
            self.add_image(secret_index, 'secret')
        except IndexError:
            # start / restart
            self.start()

    def poprandomendroom(self):
        indexes = list(range(len(self.endrooms)))
        room_index = random.choice(indexes)
        self.endrooms.pop(room_index)
        return room_index

    def picksecretroom(self):
        for e in range(901):
            x = random.choice(range(1, 10))
            y = random.choice(range(2, 9))
            index = y * 10 + x

            if self.floorplan[index]:
                continue

            if (self.boss == index - 1
                or self.boss == index + 1
                or self.boss == index + 10
                or self.boss == index - 10
            ):
                continue

            ncount = self.ncount(index)
            if (ncount >= 3
                or (ncount >= 2 and e > 300)
                or (ncount >= 1 and e > 600)
            ):
                return index


class Screen:

    def __init__(self, size, background=None):
        self.size = size
        self._surface = None
        self._background = background

    def _init(self):
        self._surface = pygame.display.set_mode(self.size)
        if self._background:
            color = self._background
        self._background = self._surface.copy()
        self._background.fill(color)

    @property
    def surface(self):
        if self._surface is None:
            self._init()
        return self._surface

    @property
    def background(self):
        if self._background is None:
            self._init()
        return self._background

    def clear(self):
        self.surface.blit(self.background, (0, 0))


class Clock:

    def __init__(self, framerate):
        self.framerate = framerate
        self._clock = pygame.time.Clock()

    def tick(self):
        return self._clock.tick(self.framerate)


def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    images = Images()
    for path in Path('img').iterdir():
        key = path.stem
        images[key] = path

    gen = IsaacGenerator(images)
    gen.start()

    pygame.display.init()
    pygame.font.init()

    screen = Screen((800, 600), background=(30,)*3)
    font = pygame.font.Font(None, 12)
    clock = Clock(60)
    timer = counter = 75

    running = True
    while running:
        elapsed = clock.tick()
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gen.start()
        #
        if (counter - elapsed) <= 0:
            gen.update()
            counter = timer
        counter -= elapsed
        # draw
        screen.clear()
        for image, pos in gen.sprites:
            screen.surface.blit(image, pos)
        pygame.display.update()

if __name__ == '__main__':
    main()
