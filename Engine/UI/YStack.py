from typing import Iterable

from pygame import Surface

from Engine.UI.Widget import IWidget

from .Widget import *

class YStack(Widget):

    def __init__(self,weights:list[float]|None = None):
        super().__init__()
        self.weights = weights or [0]
        self.weight_sum = self.calcWeightSum()
        
    def calcWeightSum(self):
        return sum(self.weights[i%len(self.weights)] for i in range(len(self.children)))
    
    def setChildren(self,children:list[IWidget]):
        self.children = children
        self.weight_sum = self.calcWeightSum()
    
    def getMinWidth(self):
        return max(c.getMinWidth() for c in self.children)
    
    def getMaxWidth(self):
        return min(c.getMaxWidth() for c in self.children)
    
    def getMinHeight(self):
        return sum(c.getMinHeight() for c in self.children)
    
    def getMaxHeight(self):
        return sum(c.getMaxHeight() for c in self.children)
    
    def updateSize(self, width: int, height: int):
        super().updateSize(width, height)
        for i,child in enumerate(self.children):
            weight = self.weights[i%len(self.weights)]
            dynamic_height = int(weight * height/self.weight_sum) if weight else 0
            min_height = child.getMinHeight()
            child_height = max(dynamic_height,min_height)
            
            child.updateSize(width,child_height)
            
    def updatePos(self, x: int, y: int):
        super().updatePos(x, y)
        dy = 0    
        for child in self.children:
            child.updatePos(x,y+dy)
            dy += child.rect.height
            
    def draw(self, surf: Surface):
        for child in self.children:
            child.draw(surf)
    