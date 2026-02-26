from Engine import *
import numpy as np
from Engine.VerletPhysics import VerletPhysics
from Scripts.Camera import Camera
from Engine import Drawable
class Edge:
    a:int
    b:int
    length:float

class Map(BaseSystem):
    def __init__(self):
        self.world = VerletPhysics(0,0.2)
        self.edges:list[Edge] = []
        
        self.node_surf = self.engine.assetManager.get('Assets/web_node.asset',pygame.Surface)
        
    def onEngineEvent(self, event):
        if event == EngineEvent.STARTED:
            self.onStart()

    def onStart(self):
        pass

    def update(self):
        for edge in self.edges:
            pass

    def draw(self):
        camera = self.engine.getSystem(Camera)
        
        self.engine.draw(
            Drawable.FBlits([zip]) 
        )
        for node in self.world.pos + camera.offset:
            pass