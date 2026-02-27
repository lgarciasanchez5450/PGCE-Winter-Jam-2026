import typing
from Engine import *
from Engine.VerletPhysics import VerletPhysics
from Engine.Serialize import Writer, Reader
from Scripts.Camera import Camera
class Edge:
    a:int
    b:int
    length:float


class Map(BaseSystem[VerletPhysics,list[Edge]]):
    def setState(self,world:VerletPhysics,edges:list[Edge]):
        self.world = world
        self.edges = edges
    
    def getState(self) -> tuple[VerletPhysics, list[Edge]]:
        return self.world,self.edges
    
    def init(self):
        self.node_surf = self.engine.assetManager.get('Assets/web_node.asset',pygame.Surface)
        
    def onEngineEvent(self, event):
        if event == EngineEvent.STARTED:
            self.onStart()

    def onStart(self):
        pass

    def update(self):
        for edge in self.edges:
            pass

    def draw(self):
        # camera = self.engine.getSystem(Camera)

        # self.engine.draw(
        #     Drawable.FBlits([(self.node_surf,pos) for pos in self.world.pos+camera.offset]) 
        # )
        pass
        
        
    # def serialize(self, writer: Writer):
    #     super().serialize(writer)
    #     self.world.serialize(writer)
    #     writer.write([(e.a,e.b,e.length) for e in self.edges])
        
    # @classmethod
    # def deserialize(cls, reader: Reader) -> tuple[tuple[typing.Any, ...], dict[str, typing.Any]]:
    #     args,kwargs = super().deserialize(reader)
    #     world = VerletPhysics.deserialize(reader)
    #     edges = reader.read(list[tuple[int,int,float]])
    #     return args+(world,edges),kwargs