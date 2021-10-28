import argparse
import os
import random

from contextlib import redirect_stdout
from pathlib import Path

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

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

    def __init__(self, sourceimages, minrooms=7, maxrooms=15):
        self.sourceimages = sourceimages
        self.minrooms = minrooms
        self.maxrooms = maxrooms
        self.floorplan_count = 0
        self.floorplan = [0 for _ in range(101)]
        self.cellqueue = []
        self.images = []
        self.started = False
        self.endrooms = []
        self.placed_special = False

    def start(self):
        self.started = True
        self.visit(45)

    def visit(self, index):
        if self.floorplan[index]:
            return False

        neighbors = self.ncount(index)
        if neighbors > 1:
            return False

        if self.floorplan_count >= self.maxrooms:
            return False

        self.cellqueue.append(index)
        self.floorplan[index] = 1
        self.floorplan_count += 1

        self.add_image(self, index, 'cell')

    def add_image(self, index, name):
        x = index % 10
        y = (i - x) / 10
        # x, y appear to be where to place on "screen"
        image = self.sourceimages[name]
        self.images.append(image)
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
        elif not self.placed_special:
            if self.floorplan_count < self.minrooms:
                # start / restart
                self.start()
                return

            self.placed_special = True
            boss = self.endrooms.pop()
            image = self.sourceimages.boss
            # image.x += 1

            try:
                reward_index = self.poprandomendroom()
                image = self.sourceimages.reward
                self.add_image(reward_index, 'reward')

                coin_index = self.poprandomendroom()
                self.add_image(coin_index, 'coin')

                secret_index = self.poprandomendroom()
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


def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    images = Images()
    images.cell = Path('img/cell.png')
    images.boss = Path('img/boss.png')
    images.reward = Path('img/reward.png')
    images.coin = Path('img/coin.png')
    images.secret = Path('img/secret.png')

if __name__ == '__main__':
    main()
