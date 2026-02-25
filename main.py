import pygame
import Drawable
from Engine import Game
from System import BaseSystem
from collections import defaultdict


class Camera(BaseSystem):
    __slots__ = 'pos','offset'
    def __init__(self,pos:pygame.Vector2) -> None:
        self.pos = pos
        self.offset = self.pos        
        
    def update(self): 
        screen_size = self.engine.window.size
        self.offset = (
            -self.pos.x.__floor__() + screen_size[0]//2,
            -self.pos.y.__floor__() + screen_size[1]//2
        )

    def draw(self): pass

class Character(BaseSystem):
    def __init__(self,pos:pygame.Vector2):
        self.pos = pos
        self.k_up = pygame.K_w
        self.k_down = pygame.K_s
        self.k_right = pygame.K_d
        self.k_left = pygame.K_a
        
    def update(self):
        keys = pygame.key.get_pressed()
        dy = keys[self.k_up] - keys[self.k_down]
        dx = keys[self.k_right] - keys[self.k_left]
        self.pos.x += dx * 3
        self.pos.y += -dy * 3
        
    def draw(self):
        r = pygame.Rect(0,0,10,10)
        camera = self.engine.getSystem(Camera)
        r.center = self.pos + camera.offset
        self.engine.draw(Drawable.Rect('white',r))

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.window_clear_color = 0
    
    game.addSystem(Camera,'Camera1',pygame.Vector2(0,0))
    game.addSystem(Character,'System1',pygame.Vector2(0,0))
    game.run()