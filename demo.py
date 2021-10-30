import argparse
import random

from pathlib import Path

from external import pygame
from floorplan.generators import BorisFloorplanGenerator
from floorplan.renderers import BorisFloorplanRenderer
from pygamelib import Clock
from pygamelib import Screen
from pygamelib import demo_generator

GENMAP = {
    'boris': BorisFloorplanGenerator,
}

RENDERERMAP = {
    'boris': BorisFloorplanRenderer,
}

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generator', choices=list(GENMAP))
    args = parser.parse_args(argv)

    if not args.generator:
        args.generator = 'boris'

    gen_class = GENMAP[args.generator]
    gen_renderer_class = RENDERERMAP[args.generator]

    generator = gen_class()
    renderer = gen_renderer_class()

    generator.start()
    demo_generator(generator, renderer)

if __name__ == '__main__':
    main()
