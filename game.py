from typing import Any
import pygame
from Engine import *
from Engine.VerletPhysics import VerletPhysics
from Scripts.Character import Character
from Scripts.Map import Map
from Scripts.Camera import Camera
from Scripts import SerializeHelper

class Game(BaseSystem[()]):
    
    def setState(self): 
        return
    def getState(self):
        return ()
        
    
    def init(self):
        # self.camera = self.engine.getSystem(Camera)
        # self.character = self.engine.getSystem(Character)
        self.map = self.engine.getSystem(Map)
        self.scene = 'start'
        
    def switchScene(self):
        if self.scene == 'start':
            self.engine.systems.clear()
            self.scene = 'game'
        if self.scene == 'game':
            self.engine.systems.clear()
            
        
    def update(self):
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_ESCAPE]:
            engine_state = self.engine.getState()
            
            print(engine_state)
            print(engine_state.serialize())
            print(EngineState.deserialize(engine_state.serialize()))
        pass
        # self.map.world.append()
        
        
def main():
    window = pygame.Window()
    engine = Engine(window.get_surface())
    engine.addSystem(Game,'')
    engine.addSystem(Camera,'',pygame.Vector2())
    engine.addSystem(Character,'',pygame.Vector2())
    engine.addSystem(Map,'',VerletPhysics(0,0.2),[])
    engine.Initialize()
    clock = pygame.Clock()
    engine.running = True
    engine.broadcastEvent(EngineEvent.STARTED)
    while engine.running:
        
        engine.Update(pygame.event.get())
        engine.screen.fill('black')
        engine.Draw()
        window.flip()
        engine.dt = clock.tick(60) / 1_000
           
if __name__ == '__main__':
    pygame.init()
    main()