import typing
import pygame
from collections import defaultdict
from .System import BaseSystem
from .Asset.Manager import AssetManager
from .Drawable import Drawable
from .Serialize import Reader, Writer,isSerializeable
__all__ = [
    'Engine','EngineEvent'
]

TT = typing.TypeVarTuple('TT')
TBS = typing.TypeVar('TBS',bound=BaseSystem)
class EngineEvent:
    INITIALIZED = 1
    STARTED = 2
    STOPPED = 3

class EngineState:
    systems:list[tuple[str,str,tuple]]

    def serialize(self) -> bytes:
        writer = Writer()
        writer.writeInt(len(self.systems))
        for fqn,name,state in self.systems:
            writer.writeStr(fqn)
            writer.writeStr(name)
            writer.writeInt(len(state))
            for item in state:
                writer.write(type(item))
                writer.write(item)
        # writer.printDebug()
        return writer.buf
    
    def __repr__(self):
        return repr(self.systems)
    
    def __eq__(self,other:typing.Any) -> bool:
        if not isinstance(other,EngineState): return False
        return self.systems == other.systems
    @classmethod
    def deserialize(cls,b:bytes) -> 'EngineState':
        reader = Reader(b)
        num_systems = reader.readInt()
        systems:list[tuple[str,str,tuple[typing.Any,...]]] = []
        for _ in range(num_systems):
            fqn = reader.readStr()
            name = reader.readStr()
            state_len = reader.readInt()
            state:list[typing.Any] = []
            for _ in range(state_len):
                typ = reader.readType()
                obj = reader.read(typ)
                state.append(obj)
            systems.append((fqn,name,tuple(state)))

        e_state = EngineState()
        e_state.systems = systems
        return e_state

class Engine:
    systems:list[BaseSystem]
    layers:defaultdict[int,list[Drawable]]
    dt:float
    def __init__(self):
        self.window = pygame.Window()
        self.window.get_surface()
        self.running = False
        self.initialized = False
        self.systems = []
        self.layers = defaultdict(list)
        self.clock = pygame.Clock()
        self.dt = 0
        self.window_clear_color:pygame.typing.ColorLike|None = None
        self.assetManager = AssetManager()

   
    def draw(self,drawable:Drawable,layer:int=0):
        self.layers[layer].append(drawable)
        
    def getSystem(self,type_:type[TBS],name:str|None=None) -> TBS:
        for system in self.systems:
            if type(system) is not type_:
                continue
            if name is not None:
                if system.name != name:
                    continue
            return system
        raise LookupError
       
    def addSystem(self,typ:type[BaseSystem[*TT]],name:str,*args:*TT):
        system = typ(self,name)
        system.setState(*args)
        if self.initialized:
            system.init()
        self.systems.append(system)
        return system

    def removeSystem(self,system:BaseSystem):
        self.systems.remove(system)

    def getState(self) -> EngineState:
        e_state = EngineState()
        e_state.systems = []
        for system in self.systems:
            state = system.getState()
            if not isSerializeable(state):
                raise RuntimeError(f'Serialization Error: System \'{type(system).__name__}\' returned an unserializable state: {repr(state)}')
            e_state.systems.append((str(system._fqn),str(system.name),state))
        return e_state
    
    def loadState(self,state:EngineState):
        for sys_fqn,sys_name,sys_state  in state.systems:
            system_cls = BaseSystem._fqn_to_cls[sys_fqn]
            self.addSystem(system_cls,sys_name,*sys_state)
        

    def _broadcastEngineEvent(self,event):
        for system in self.systems:
            system.onEngineEvent(event)
          
            
    def initialize(self):
        self.initialized = True
        for system in self.systems:
            system.init()
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
            
                
                