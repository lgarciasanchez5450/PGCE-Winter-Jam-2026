import typing
from pygame import Rect


__all__ = ['IWidget','Widget']


class IWidget(typing.Protocol):
    @property
    def rect(self) -> Rect: ...
    
    def getMinWidth(self) -> int: ...
    
    def getMaxWidth(self) -> int: ...
    
    def getMinHeight(self) -> int: ...
    
    def getMaxHeight(self) -> int: ...
    
    def updateSize(self,width:int,height:int): ...
    
    def updatePos(self,x:int,y:int): ...
    
    

class Widget:
    rect:Rect
    def __init__(self) -> None:
        self.rect = Rect()
        
    def updateSize(self,width:int,height:int):
        self.rect.width = width
        self.rect.height = height
    
    def updatePos(self,x:int,y:int): 
        self.rect.x = x
        self.rect.y = y
    
    def getMinWidth(self) -> int:
        return 0
    
    def getMaxWidth(self) -> int:
        return (1<<64) - 1
    
    def getMinHeight(self) -> int:
        return 0
    
    def getMaxHeight(self) -> int:
        return (1<<64) - 1
