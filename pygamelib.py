from external import pygame

class Screen:

    def __init__(self, size, background=None):
        self.size = size
        self._surface = None
        self._rect = None
        self._background = background

    def _init(self):
        self._surface = pygame.display.set_mode(self.size)
        if self._background:
            color = self._background
        self._rect = self._surface.get_rect()
        self._background = self._surface.copy()
        self._background.fill(color)

    @property
    def rect(self):
        if self._rect is None:
            self._init()
        return self._rect

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


def demo_generator(generator, renderer):
    """
    :param generator: has `.update` and `.start` methods and `.status.label` attribute.
    :param renderer: `.render(floorplan)`
    """
    from floorplan.generators import GeneratorStatus

    pygame.display.init()
    pygame.font.init()

    screen = Screen((800, 600), background=(10,)*3)
    font = pygame.font.Font(None, 52)
    clock = Clock(60)
    timer = counter = 75

    errors = (GeneratorStatus.MINROOM_NOT_REACHED, GeneratorStatus.UNABLE_TO_FINALIZE)

    pause_for_status = False
    running = True
    while running:
        elapsed = clock.tick()
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    generator.start()
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_r:
                    pause_for_status = not pause_for_status
                elif event.key == pygame.K_a:
                    timer += 5
                elif event.key == pygame.K_z:
                    timer -= 5
        # update
        if not pause_for_status and generator.status in errors:
            generator.start()
            counter = timer
        else:
            if (counter - elapsed) <= 0:
                generator.update()
                counter = timer
        counter -= elapsed
        # draw
        screen.clear()
        renderer(screen.surface, generator)
        # help message
        image = font.render('space to restart', True, (200,)*3)
        screen.surface.blit(image, image.get_rect(bottomright = screen.rect.bottomright))
        # timer display
        image = font.render(str(timer), True, (200,)*3)
        screen.surface.blit(image, image.get_rect(topleft = screen.rect.topleft))
        # demo states
        image = font.render(f'Pause for status (r): {pause_for_status}', True, (200,)*3)
        screen.surface.blit(image, image.get_rect(bottomleft = screen.rect.bottomleft))
        # draw - generator status
        pygame.display.update()
