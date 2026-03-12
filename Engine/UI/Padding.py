from .Widget import *

class Padding(Widget):
    child:IWidget
    def __init__(self,child:IWidget,pad:list[int]):
        super().__init__()
        self.child = child
        if len(pad) == 1:
            pad = pad * 4
        elif len(pad) == 2:
            pad = pad * 2
        elif len(pad) == 3:
            pad = [pad[0],pad[1],pad[2],pad[1]]
        elif len(pad) == 4:
            pass
        else:
            raise ValueError(f'Unsupported Pad Value: {pad}')
            
        self.padding_top, \
        self.padding_right,\
        self.padding_bottom,\
        self.padding_left = pad

    def setChild(self,child:IWidget):
        self.child = child
        
    def getMinWidth(self) -> int:
        return self.padding_left + self.padding_right + self.child.getMinWidth()
        
    def getMaxWidth(self) -> int:
        return self.padding_left + self.padding_right + self.child.getMaxWidth()
    
    def getMinHeight(self) -> int:
        return self.padding_top + self.padding_bottom + self.child.getMinHeight()
        
    def getMaxHeight(self) -> int:
        return self.padding_top + self.padding_bottom + self.child.getMaxHeight()
    
    def updateSize(self, width: int, height: int):
        super().updateSize(width, height)
        self.child.updateSize(
            width-self.padding_left-self.padding_right,
            height-self.padding_top-self.padding_bottom
        )
    
    def updatePos(self, x: int, y: int):
        super().updatePos(x, y)
        self.child.updatePos(
            x + self.padding_left,
            y + self.padding_top
        )