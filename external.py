import os

from contextlib import redirect_stdout

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

del os
del redirect_stdout
