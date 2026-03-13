import typing
import os
import sys
from .Serialize import Writer, Reader
from .Events import *
if typing.TYPE_CHECKING:
    from Engine import Scene
def _cls_module_path(cls:type):
    return os.path.abspath(sys.modules[cls.__module__].__file__ or '')

_fqn_to_cls:dict[str,type['BaseSystem']] = {}
class BaseSystem[*T]:
    _fqn_to_cls = _fqn_to_cls
    name:str
    engine:'Scene'
    _fqn:str = 'BaseSystem'
    __slots__ = 'name','engine','event_map'
    
    def __init_subclass__(cls) -> None:
        necessary_attrs = []#['serialize','deserialize']
        for attr in necessary_attrs:
            assert attr in cls.__dict__, f'System {repr(cls.__name__)} missing required method: {attr}\nFile: {_cls_module_path(cls)}'
        parent = cls.mro()[0]
        parent_fqn = getattr(parent,'_fqn',None)
        assert parent_fqn is not None
        cls._fqn = f'{parent_fqn}.{cls.__name__}'
        assert cls._fqn not in _fqn_to_cls, f'System FQN Clash {repr(cls._fqn)}\nFile A: {_cls_module_path(cls)}\nFile B: {_cls_module_path(_fqn_to_cls[cls._fqn])}'
        _fqn_to_cls[cls._fqn] = cls

    def __init__(self,engine:'Scene',name:str):
        self.engine = engine
        self.name = name
        self.event_map:dict[int,typing.Callable[...,typing.Any]] = {}
      
    def addHook[E:BaseEvent](self,event:type[E],func:typing.Callable[[E],typing.Any]):
        if event.type in self.event_map:
            raise RuntimeError(f'Multiple Callbacks for event {event.__name__} [{event.type}]')
        self.event_map[event.type] = func
        
    def onEvent(self,event:pygame.Event):
        hook = self.event_map.get(event.type)
        if hook is not None:
            return hook(event)
        return False
    
    def onEngineEvent(self,event): ... #gets called misc. engine events
    
    def init(self): ... #on initialization
    
    def stop(self): ... #on stop #no other function will be called until init
    
    def update(self): ... #on every frame
    
    def draw(self): ... # on every frame

    def setState(self,*state:*T): raise NotImplementedError(f'{repr(type(self))} must define .setState(*args)')
    
    def getState(self) -> tuple[*T]: raise NotImplementedError(f'{repr(type(self))} must define .getState()')
    