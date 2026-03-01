import typing
import math
from Engine import *
from Engine.VerletPhysics import VerletPhysics
from Engine.Serialize import Writer, Reader,addSerializable
from Scripts.Camera import Camera
from gameSim import GameState,Edge,Node
import numpy as np
import gameSim

def serializeNode(writer:Writer,node:Node):
    writer.writeInt(int(node.explosion_time))
    writer.writeInt(int(node.freeze_time))

def deserializeNode(reader:Reader) -> Node:
    out = Node()
    out.explosion_time = reader.readInt()
    out.freeze_time = reader.readInt()
    return out

addSerializable(Node,serializeNode,deserializeNode)

def serializeEdge(writer:Writer,edge:Edge):
    writer.writeInt(int(edge.a_node))
    writer.writeInt(int(edge.b_node))
    writer.write([bool(b) for b in edge.cycle])

def deserializeEdge(reader:Reader):
    edge = Edge()
    edge.a_node = reader.readInt()
    edge.b_node = reader.readInt()
    edge.cycle = reader.readList(bool)
    return edge

addSerializable(Edge,serializeEdge,deserializeEdge)

def serializeGameState(writer:Writer,gs:GameState):
    writer.writeInt(int(gs.start_node))
    writer.writeInt(int(gs.end_node))
    writer.writeInt(int(gs.start_tick))
    writer.write(list(gs.nodes))
    writer.write(list(gs.edges))

def deserializeGameState(reader:Reader):
    gs = GameState()
    gs.start_node = reader.readInt()
    gs.end_node = reader.readInt()
    gs.start_tick = reader.readInt()
    gs.nodes = reader.readList(Node)
    gs.edges = reader.readList(Edge)
    return gs

addSerializable(GameState,serializeGameState,deserializeGameState)

class Map(BaseSystem[GameState,int,bytes]):
    
    def setState(self,gs:GameState,tick:int,path:bytes):
        print(f'{gs=}, {tick=}, {path=}')
        
        self.gs = gs
        self.tick = tick
        self.path = list(path)
        self.node_to_pos:list[pygame.Vector2] = []
        len_nodes = len(self.gs.nodes)
        r = 100
        theta_offset = math.pi / 2
        for i in range(len_nodes):
            theta = (i*2*math.pi +theta_offset)/ len_nodes
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            self.node_to_pos.append(pygame.Vector2(x,y))
        self.node_pos = VerletPhysics(len(self.gs.nodes),0.1)
        self.node_pos.setPositions(self.node_to_pos,sync_vel=True)
        self.time = 0

    def getState(self):
        return self.gs,self.tick,bytes(self.path),
    
    def init(self):
        
        self.gs_gen = gameSim.generateInterestingGameStates(4,10,5,7,2,2,False)
        self.node_surf = self.engine.assetManager.get('Assets/web_node.asset',pygame.Surface)
        self.ofst = (-self.node_surf.width//2,-self.node_surf.height//2)

    def onEngineEvent(self, event):
        if event == EngineEvent.STARTED:
            self.onStart()

    def onStart(self):
        pass

    def update(self):
        self.time += self.engine.dt
        t_mult = (np.sin(self.time)*2 + 1)/2# 2*np.sin(self.time) / self.time + 1
        accel = np.zeros((self.node_pos.capacity,2))
        for edge in self.gs.edges:
            a_node = edge.a_node
            b_node = edge.b_node
            a_pos = self.node_pos.get(a_node)
            b_pos = self.node_pos.get(b_node)
            dif = a_pos - b_pos
            length = np.sqrt(dif*dif)
            norm = dif / length
            norm *= length * t_mult
            accel[self.node_pos.id_to_ind[a_node]] -= norm
            accel[self.node_pos.id_to_ind[b_node]] += norm
        
        repel_dist = 100
        strength = 100
        for i in range(len(self.node_pos.pos)):
            for j in range(i+1,len(self.node_pos.pos),1):
                dif = self.node_pos.pos[i] - self.node_pos.pos[j]
                length = np.sqrt(dif*dif)
                mult = length / repel_dist
                mult *= mult
                mult = 1-mult
                mult[mult<0] = 0
                norm = dif / length
                norm *= mult * strength
                accel[i] += norm
                accel[j] -= norm
        self.node_pos.update(accel)
        keysd = pygame.key.get_just_pressed()
        if keysd[pygame.K_SPACE]:
            
            state,(start,end,tick,path) = self.gs_gen.__next__() # next(self.gs_gen)
            state.start_node = start
            state.end_node = end
            state.start_tick = tick
            self.setState(state,0,bytes(path))
                
            
    def draw(self):
        try:
            camera_offset = self.engine.getSystem(Camera).offset
        except LookupError:
            camera_offset = (0,0)
        for edge in self.gs.edges:
            a_pos = self.node_pos.get(edge.a_node)
            b_pos = self.node_pos.get(edge.b_node)
            self.engine.draw(Drawable.Line('white',a_pos+camera_offset,b_pos+camera_offset,3),layer=1)
        
        self.engine.draw(Drawable.Lines('red',False,self.node_pos.pos[self.path]+camera_offset,2),layer=1)

        self.engine.draw(Drawable.FBlits([(self.node_surf,pos) for pos in self.node_pos.pos+camera_offset+self.ofst]),layer=2)