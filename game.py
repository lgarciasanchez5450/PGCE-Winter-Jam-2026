import pygame
from Engine import *

from Scripts.Character import Character
from Scripts.Map import Map
from Scripts.Camera import Camera

class Game(BaseSystem):
    pass

if __name__ == '__main__':
    pygame.init()
    game = Engine()
    game.window_clear_color = 0

    game.addSystem(Camera,'',pygame.Vector2())
    game.addSystem(Character,'',pygame.Vector2())
    game.addSystem(Map,'')

    game.run()