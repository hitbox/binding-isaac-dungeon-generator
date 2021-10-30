from pathlib import Path

from external import pygame

class Images:
    """
    Dict-like with attribute access, set item as path, get item as pygame.Surface.
    """
    image_loader = pygame.image.load

    def __init__(self):
        self._images = {}

    def __setitem__(self, key, path):
        if key in self._images:
            raise KeyError(f'{key} already set.')
        self._images[key] = path

    def __getitem__(self, key):
        path = self._images[key]
        if isinstance(path, (str, Path)):
            self._images[key] = self.image_loader(path)
        return self._images[key]

    def __setattr__(self, key, path):
        # this is probably not how to do this best
        if key != '_images':
            self[key] = path
        else:
            super().__setattr__(key, path)

    def __getattr__(self, key):
        return self[key]

    @classmethod
    def from_dir(cls, path):
        inst = cls()
        for path in Path(path).iterdir():
            key = path.stem
            inst[key] = path
        return inst
