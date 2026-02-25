from Engine import * 

class Camera(BaseSystem):
    __slots__ = 'pos','offset'
    def __init__(self,pos:pygame.Vector2) -> None:
        self.pos = pos
        self.offset = self.pos        
        
    def update(self): 
        screen_size = self.engine.window.size
        self.offset = (
            -self.pos.x.__floor__() + screen_size[0]//2,
            -self.pos.y.__floor__() + screen_size[1]//2
        )

    def draw(self): pass
