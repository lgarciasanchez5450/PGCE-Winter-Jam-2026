import typing
if typing.TYPE_CHECKING:
    from Engine import Game

class BaseSystem:
    name:str
    engine:'Game'
    __slots__ = 'name','engine'
    
    def onEngineEvent(self,event): ...
    
    def update(self): raise NotImplementedError
    
    def draw(self): raise NotImplementedError