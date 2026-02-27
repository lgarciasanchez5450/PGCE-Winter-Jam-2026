from typing import Any, Callable

from Engine.Serialize import Reader, Writer
from Scripts.Camera import Camera
from Engine import *
class Character(BaseSystem[pygame.Vector2]):
    def getState(self):
        return (self.pos,)
    
    def setState(self,pos:pygame.Vector2):
        self.pos = pos
        
    def init(self):
        self.k_up = pygame.K_w
        self.k_down = pygame.K_s
        self.k_right = pygame.K_d
        self.k_left = pygame.K_a
        
    def update(self):
        keys = pygame.key.get_pressed()
        dy = keys[self.k_up] - keys[self.k_down]
        dx = keys[self.k_right] - keys[self.k_left]
        self.pos.x += dx * 3
        self.pos.y += -dy * 3
        
    def draw(self):
        r = pygame.Rect(0,0,10,10)
        camera = self.engine.getSystem(Camera)
        r.center = self.pos + camera.offset
        
        self.engine.draw(Drawable.Rect('white',r))

    # def serialize(self, writer: Writer):
    #     super().serialize(writer)
    #     writer.writeFloat(float(self.pos.x))
    #     writer.writeFloat(float(self.pos.y))
        
    # @classmethod
    # def deserialize(cls, reader: Reader) -> tuple[tuple[Any, ...], dict[str, Any]]:
    #     args,kwargs = super().deserialize(reader)
    #     x = reader.readFloat()
    #     y = reader.readFloat()
    #     pos = pygame.Vector2(x,y)
    #     return args+(pos,),kwargs