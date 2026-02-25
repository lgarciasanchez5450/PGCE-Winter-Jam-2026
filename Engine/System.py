import typing
if typing.TYPE_CHECKING:
    from Engine import Engine

class BaseSystem:
    name:str
    engine:'Engine'
    __slots__ = 'name','engine'
    
    def onEngineEvent(self,event): ...
    
    def update(self): ...
    
    def draw(self): ...