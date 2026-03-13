import typing
import pygame
from collections import defaultdict
from .System import BaseSystem
from .Asset.Manager import AssetManager
from .Drawable import Drawable
from .Serialize import Reader, Writer,isSerializeable
from .EventManager import EventManager
from . import Async
__all__ = [
    'Scene','EngineEvent','EngineState'
]

class EngineEvent:
    INITIALIZED = 1
    STARTED = 2
    STOPPED = 3

class EngineState:
    systems:list[tuple[str,str,tuple]]
    
    def __init__(self):
        self.systems = []

    def serialize(self) -> bytes:
        writer = Writer()
        writer.writeInt(len(self.systems))
        for fqn,name,state in self.systems:
            writer.writeStr(fqn)
            writer.writeStr(name)
            writer.writeInt(len(state))
            for item in state:
                writer.writeType(item)
                writer.write(item)
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

    def setSystemArgs[*TT](self,typ:type[BaseSystem[*TT]],name:str,*args:*TT):
        for i,(fqn,sys_name,_) in enumerate(self.systems):
            if typ._fqn == fqn and name == sys_name:
                self.systems[i] = (fqn,sys_name,args)
                return
        raise LookupError
    
    def addSystem[*TT](self,typ:type[BaseSystem[*TT]],name:str,*args:*TT):
        if not isSerializeable(args):
            raise RuntimeError(f'Serialization Error: System \'{typ.__name__}\' returned an unserializable state: {repr(args)}')
        self.systems.append((str(typ._fqn),str(name),args))
        
class Scene:
    systems:list[BaseSystem]
    layers:defaultdict[int,list[Drawable]]
    dt:float
    def __init__(self,viewport:pygame.Surface,assets:AssetManager):
        self.screen = viewport
        self.started = False
        self.systems = []
        self.layers = defaultdict(list)
        self.dt = 0
        self.assets = assets
        self.async_ctx = Async.Context()

        
    def draw(self,drawable:Drawable,layer:int=0):
        self.layers[layer].append(drawable)

    def getSystem[BS:BaseSystem](self,type_:type[BS],name:str|None=None) -> BS:
        for system in self.systems:
            if type(system) is not type_:
                continue
            if name is not None:
                if system.name != name:
                    continue
            return system
        raise LookupError
       
    def addSystem[*TT](self,typ:type[BaseSystem[*TT]],name:str,*args:*TT):
        system = typ(self,name)
        system.setState(*args)
        if self.started:
            system.init()
        self.systems.append(system)
        return system

    def removeSystem(self,system:BaseSystem):
        self.systems.remove(system)

    def startCoroutine(self,coro:typing.Generator|typing.Awaitable):
        self.async_ctx.add(coro) # pyright: ignore[reportArgumentType]
        
    def stopCoroutine(self,coro:typing.Generator|typing.Awaitable):
        self.async_ctx.remove(coro) # pyright: ignore[reportArgumentType]
        
    def checkCoroutine(self,coro:typing.Generator|typing.Awaitable):
        return self.async_ctx.isAlive(coro) # pyright: ignore[reportArgumentType]

    def getState(self) -> EngineState:
        state = EngineState()
        for system in self.systems:
            state.addSystem(type(system),system.name,system.getState())
        return state
    
    def loadState(self,state:EngineState):
        for sys_fqn,sys_name,sys_state  in state.systems:
            system_cls = BaseSystem._fqn_to_cls[sys_fqn]
            self.addSystem(system_cls,sys_name,*sys_state)
        
    def clearState(self):
        self.systems.clear()
        self.started = False

    def broadcastEvent(self,event):
        for system in self.systems:
            system.onEngineEvent(event)   
       
    ### Methods only for Engine owner ###   
    
    def Start(self):
        if self.started: return False
        for system in self.systems:
            system.init()
        self.started = True
        self.broadcastEvent(EngineEvent.INITIALIZED)
        return True
        
    def Stop(self):
        if not self.started: return False
        for system in self.systems:
            system.stop()
        self.started = False
        self.broadcastEvent(EngineEvent.STOPPED)
        return True
    
    def handleEvent(self,event:pygame.Event):
        for system in self.systems:
            if system.onEvent(event): return True
        return False

    def Update(self,keys:pygame.key.ScancodeWrapper,keys_down:pygame.key.ScancodeWrapper,keys_up:pygame.key.ScancodeWrapper):
        if not self.started: raise RuntimeError(f'Update Before Start')
        self.keys = keys
        self.keys_down = keys_down
        self.keys_up = keys_up
        
        for system in self.systems:
            system.update()
        for system in self.systems:
            system.draw()
        self.async_ctx.tick()
        
    def Draw(self):
        if not self.started: raise RuntimeError(f'Draw Before Start')
        for layer_num in sorted(self.layers.keys()):
            for drawable in self.layers[layer_num]:
                drawable.draw(self.screen)
        self.layers.clear()

    def SetViewport(self,viewport:pygame.Surface):
        self.screen = viewport
        
