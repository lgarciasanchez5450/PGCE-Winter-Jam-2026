import typing
import pygame
from collections import defaultdict
from .System import BaseSystem
from . import Drawable
from .AssetLoading.AssetLoader import AssetManager
__all__ = [
    'Engine','EngineEvent','BaseSystem','pygame','Drawable'
]

TS = typing.TypeVar('TS',bound=BaseSystem)
P = typing.ParamSpec('P')
class EngineEvent:
    INITIALIZED = 1
    STARTED = 2
    STOPPED = 3

class Engine:
    systems:list[BaseSystem]
    layers:defaultdict[int,list[Drawable.Drawable]]
    dt:float
    # __slots__ = 'window','running','systems','layers','clock','dt','window_clear_color','events'
    def __init__(self):
        self.window = pygame.Window()
        self.running = False
        self.initialized = False
        self.systems = []
        self.layers = defaultdict(list)
        self.clock = pygame.Clock()
        self.dt = 0
        self.window_clear_color:pygame.typing.ColorLike|None = None
        self.assetManager = AssetManager()

        self.on_initialize_callbacks:list[typing.Callable[[],typing.Any]] = []

    def draw(self,drawable:Drawable.Drawable,layer:int=0):
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
        system._params = args,kwargs
        if self.initialized:
            system.__init__(*args,**kwargs)
        self.systems.append(system)
        return system

    def removeSystem(self,system:BaseSystem):
        self.systems.remove(system)
        
    def _broadcastEngineEvent(self,event):
        for system in self.systems:
            system.onEngineEvent(event)
            
    def initialize(self):
        self.initialized = True
        for system in self.systems:
            args,kwargs = system._params
            system.__init__(*args,**kwargs)
        self._broadcastEngineEvent(EngineEvent.INITIALIZED)
        

    def run(self):
        if not self.initialized:
            self.initialize()
        self.running = True
        screen = self.window.get_surface()
        self._broadcastEngineEvent(EngineEvent.STARTED)
        while self.running:
            self.events = pygame.event.get()
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
            
                
                