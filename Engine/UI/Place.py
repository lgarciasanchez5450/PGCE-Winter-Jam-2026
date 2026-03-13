from .Widget import *
from pygame import Surface
class Place(WidgetUnary):
    def __init__(self,child:IWidget,x:float=0,y:float=0,w:float=0,h:float=0) -> None:
        super().__init__()
        self.setChild(child)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
    def getMinWidth(self) -> int:
        return self.child.getMinWidth()
    
    def getMinHeight(self) -> int:
        return self.child.getMinHeight()
    
    def updateSize(self, width: int, height: int):
        super().updateSize(width, height)
        self.child.updateSize(
            max((self.getMinWidth(),int(self.w*width))),
            max((self.getMinHeight(),int(self.h*height))),
        )
            
    def updatePos(self, x: int, y: int):
        super().updatePos(x, y)
        offset_x = int((self.rect.width - self.child.rect.width) * self.x)
        offset_y = int((self.rect.height - self.child.rect.height) * self.y)
        
        self.child.updatePos(x+offset_x,y+offset_y)
    
    def draw(self, surf: Surface):
        self.child.draw(surf)
    