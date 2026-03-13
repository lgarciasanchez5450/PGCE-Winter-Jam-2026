from .Widget import *
MAX_U64 = (1<<64)-1

class Empty(Widget):
    def __init__(self,min_w:int=0,max_w:int=MAX_U64,min_h:int=0,max_h:int=MAX_U64) -> None:
        super().__init__()
        self.min_w = min_w
        self.max_w = max_w
        self.min_h = min_h
        self.max_h = max_h
        
    def getMinWidth(self) -> int:
        return self.min_w
    
    def getMaxWidth(self) -> int:
        return self.max_w
    
    def getMinHeight(self) -> int:
        return self.min_h
    
    def getMaxHeight(self) -> int:
        return self.max_h