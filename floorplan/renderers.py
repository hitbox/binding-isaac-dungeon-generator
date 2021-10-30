from external import pygame
from resources import Images

from .room import RoomType

class BorisFloorplanRenderer:
    """
    Boris rendering code stripped out to its own class.
    """

    def __init__(self):
        self._font = None
        self.images = Images.from_dir('img')

    @property
    def font(self):
        if self._font is None:
            pygame.font.init()
            self._font = pygame.font.Font(None, 30)
        return self._font

    def __call__(self, surface, generator):
        rect = surface.get_rect()
        # floor state
        for i, room in enumerate(generator.floorplan):
            if room == 0:
                continue
            x = i % 10
            y = (i - x) / 10
            cellw, cellh = self.images.cell.get_size()
            x = rect.width / 2 + cellw * (x - 5)
            y = rect.height / 2 + cellh * (y - 4)
            image = self.images[room.name.lower()]
            surface.blit(image, (x, y))
            if i in generator.endrooms:
                pygame.draw.rect(surface, (200,10,10), pygame.Rect(x,y,cellw,cellh), 1)

        # status
        image = self.font.render(generator.status.label, True, (200,)*3)
        surface.blit(image, image.get_rect(topright = rect.topright))
