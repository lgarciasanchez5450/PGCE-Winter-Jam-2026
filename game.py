import pygame
from Engine import *

from Scripts.Character import Character
from Scripts.Map import Map
from Scripts.Camera import Camera

class Game(BaseSystem):
    def __init__(self):
        self.camera = self.engine.addSystem(Camera,'',pygame.Vector2())
        self.character = self.engine.addSystem(Character,'',pygame.Vector2())
        self.map = self.engine.addSystem(Map,'')
        
    def update(self):
        pass
        # self.map.world.append()
        
if __name__ == '__main__':
    pygame.init()
    engine = Engine()
    engine.window_clear_color = 0
    engine.addSystem(Game,'')
    engine.run()