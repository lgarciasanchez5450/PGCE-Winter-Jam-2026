import typing
import pygame
from System import BaseSystem
from collections import defaultdict
from Drawable import Drawable

TS = typing.TypeVar('TS',bound=BaseSystem)
P = typing.ParamSpec('P')

class Game:
    systems:list[BaseSystem]
    layers:defaultdict[int,list[Drawable]]
    dt:float

    def __init__(self):
        self.window = pygame.Window()
        self.running = False
        self.systems = []
        self.layers = defaultdict(list)
        self.clock = pygame.Clock()
        self.dt = 0
        self.window_clear_color:pygame.typing.ColorLike|None = None
        
    def draw(self,drawable:Drawable,layer:int=0):
        self.layers[layer].append(drawable)
        
    def getSystem(self,type_:type[TS],name:str|None=None) -> TS:
        for system in self.systems:
            if type(system) is not type_:
                continue
            if name is not None:
                if system.name != name:
                    continue
            return system
        raise LookupError
       
    def addSystem(self,type_:typing.Callable[P,TS],name:str,*args:P.args,**kwargs:P.kwargs):
        system:TS = object.__new__(type_) #type: ignore
        system.name = name
        system.engine = self
        system.__init__(*args,**kwargs)
        self.systems.append(system)
        
    def _broadcastEngineEvent(self,event):
        for system in self.systems:
            system.onEngineEvent(event)
            

    def run(self):
        self.running = True
        screen = self.window.get_surface()
        while self.running:
            for event in pygame.event.get(): pass
            for system in self.systems: system.update()
            for system in self.systems: system.draw()
            
            if self.window_clear_color is not None:
                screen.fill(self.window_clear_color)
                
            for layer_num in sorted(self.layers.keys()):
                for drawable in self.layers[layer_num]:
                    drawable.draw(screen)
            self.layers.clear()
            
            self.window.flip()
            self.dt = self.clock.tick(60) / 1_000
            
                
                