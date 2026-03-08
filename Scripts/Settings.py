from Engine import *

class Settings(BaseSystem[()]):
    def setState(self):
        
        self.a = pygame.Rect()
        self.b = pygame.Rect()
    
    def getState(self) -> tuple[()]:
        return ()
    
    def init(self):
        
        pass
    
    def update(self):
        pass
    
    def draw(self):
        self.engine.draw(
            Drawable.Rect('red',pygame.Rect(50,50,50,50)),
        )
        self.engine.draw(
            Drawable.Rect('blue',pygame.Rect(50,100,50,50)),
        )
        pass
    