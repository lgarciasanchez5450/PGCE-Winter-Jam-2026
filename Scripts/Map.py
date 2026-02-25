from Engine import *
import numpy as np
from Engine.VerletPhysics import VerletPhysics

class Edge:
    a:pygame.Vector2
    b:pygame.Vector2
    length:float

class Map(BaseSystem):
    def __init__(self):
        self.nodes:list[pygame.Vector2] = []
        self.edges:list[Edge] = []

    def onEngineEvent(self, event):
        if event == EngineEvent.START:
            self.onStart()

    def onStart(self):
        pass

    def update(self):
        for edge in self.edges:
            pass

    def load(self):
        pass