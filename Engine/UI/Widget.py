import typing
from pygame import Rect, Surface, Event


__all__ = ['IWidget','Widget','WidgetUnary']


class IWidget(typing.Protocol):
    @property
    def rect(self) -> Rect: ...
    
    def getMinWidth(self) -> int: ...
    
    def getMaxWidth(self) -> int: ...
    
    def getMinHeight(self) -> int: ...
    
    def getMaxHeight(self) -> int: ...
    
    def updateSize(self,width:int,height:int): ...
    
    def updatePos(self,x:int,y:int): ...
    
    def draw(self,surf:Surface): ...
    
    def handleEvent(self,event:Event) -> bool|None: ...
        
    def iter(self) -> typing.Iterable['IWidget']: ...

class Widget:
    rect:Rect
    children:list[IWidget]
    def __init__(self) -> None:
        self.rect = Rect()
        self.children = []
        
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

    def draw(self,surf:Surface): ...
    
    def setChildren(self,children:list[IWidget]):
        self.children = children
    
    def handleEvent(self,event:Event):
        for child in self.children:
            if child.handleEvent(event):
                return True
        
    
    def iter(self) -> typing.Iterable[IWidget]: 
        yield self
        for child in self.children:
            yield from child.iter()
            
class WidgetUnary(Widget):
    child:IWidget
    def iter(self):
        yield self
        yield from self.child.iter()
        
    def setChildren(self, children: list[IWidget]): raise NotImplementedError('Unary Widget Cannot set multiple children')
    
    def setChild(self,child:IWidget):
        self.child = child
        
    def handleEvent(self, event: Event):
        if self.child.handleEvent(event):
            return True