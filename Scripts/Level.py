from Engine import *
from Scripts.Camera import Camera
from Scripts.MapDrawer import MapDrawer
from gameSim import GameState
import numpy as np

class Level(BaseSystem[GameState]):
    def getState(self) -> tuple[GameState]:
        return self.gamestate,
    
    def setState(self,gamestate:GameState):
        self.character_node = gamestate.start_node
        self.gamestate = gamestate

    def init(self):
        self.camera = self.engine.getSystem(Camera)
        self.map = self.engine.getSystem(MapDrawer)
        
        self.map.setMap(self.gamestate.nodes,self.gamestate.edges)

    def update(self):
        pass
    
    def draw(self):
        camera_offset = self.camera.offset
        character_pos = np.floor(self.map.getPos(self.character_node))
        
        self.engine.draw(
            Drawable.Rect('blue',pygame.Rect(0,0,20,20).move_to(center=character_pos).move(camera_offset),width=3),layer=3
        )