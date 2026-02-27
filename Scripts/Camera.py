import typing
from Engine import *
from Engine.Serialize import Reader, Writer 


class Camera(BaseSystem[pygame.Vector2]):
    offset:tuple[int,int]
    __slots__ = 'pos','offset'
    
    def setState(self,pos:pygame.Vector2) -> None:
        self.pos = pos
        self.offset = (int(self.pos.x),int(self.pos.y))        
        
    def getState(self):
        return (self.pos,)
        
    def update(self): 
        screen_size = self.engine.window.size
        self.offset = (
            -self.pos.x.__floor__() + screen_size[0]//2,
            -self.pos.y.__floor__() + screen_size[1]//2
        )
        
    
    # def serialize(self, writer: Writer):
    #     super().serialize(writer)
    #     writer.write(float(self.pos.x))
    #     writer.write(float(self.pos.y))

    # @classmethod
    # def deserialize(cls, reader: Reader) -> tuple[tuple[typing.Any,...],dict[str,typing.Any]]:
    #     args,kwargs = super().deserialize(reader)
    #     x = reader.readFloat()
    #     y = reader.readFloat()
    #     return (args+(pygame.Vector2(x,y),),kwargs)
    

