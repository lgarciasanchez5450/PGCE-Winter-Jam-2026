from Engine import *

class InspectorRenderer:
    def __init__(self,inspector:'Inspector'):
        self.i = inspector
        
    def draw(self,surf:pygame.Surface):
        pygame.draw.rect(surf,'gray',self.i.rect,0,5)
        pass

class Inspector(BaseSystem[pygame.Rect]):
    def setState(self,rect):
        self.rect = rect
        
    def getState(self):
        return (self.rect,)
    
    
    def init(self):
        self.renderer = InspectorRenderer(self)
        pass
    
    def draw(self):
        self.engine.draw(self.renderer)