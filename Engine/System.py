import typing
if typing.TYPE_CHECKING:
    from Engine import Engine

class BaseSystem:
    name:str
    engine:'Engine'
    _params:tuple[tuple[typing.Any,...],typing.Mapping[str,typing.Any]]
    __slots__ = 'name','engine'
    
    def onEngineEvent(self,event): ...
    
    def update(self): ...
    
    def draw(self): ...