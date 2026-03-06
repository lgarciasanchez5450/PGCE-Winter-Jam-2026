import typing
import math
from Engine import *
from Engine.VerletPhysics import VerletPhysics
from Engine.Serialize import Writer, Reader,addSerializable
from Scripts.Camera import Camera
from gameSim import GameState,Edge,Node
import numpy as np
import gameSim
import debug

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






class Map(BaseSystem[GameState,int,list[int]]):
    def setState(self,gs:GameState,tick:int,path:list[int]):
        self.gs = gs
        self.tick = tick
        self.path = path
        self.sim_time_left = 0
        self.connections:set[tuple[int,int]] = set()
        for edge in gs.edges:
            self.connections.add((edge.a_node,edge.b_node))
        
        width = max(300,20*len(gs.nodes))
        self.ind_to_pos = np.linspace(-width//2,width//2,len(self.gs.nodes))
        self.id_order = list(range(len(gs.nodes)))
        self.sort()
        print('ID Order:',self.id_order)
        self.world = VerletPhysics(0,0.1)
        len_nodes = len(gs.nodes)
        r = 100
        theta_offset = math.pi / 2
        for i in range(len_nodes):
            id = self.id_order[i]
            theta = (id*2*math.pi +theta_offset)/ len_nodes
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            self.world.append((x,y),(0,0))
            
        self.sim_cpu_time = 0
        

    def getState(self):
        return self.gs,self.tick,self.path
    
    def connecting(self,a,b):
        if b<a: a,b = b,a
        return (a,b) in self.connections
    
    def getNumCross(self) -> int:
        n = len(self.gs.nodes)
        crosses = 0
        for a in range(n): #o(n)
            aid = self.id_order[a] #o(1)
            for b in range(a+1,n,1): #o(n)
                bid = self.id_order[b] #o(1)
                if self.connecting(aid,bid): #o(1)
                    for i in range(a): 
                        iid = self.id_order[i] #o(1)
                        for j in range(a+1,b,1):
                            jid = self.id_order[j]
                            if self.connecting(iid,jid):
                                crosses += 1
        return crosses

    
    def sort(self):
        n = len(self.id_order)
        for x in range(n):
            for i in range(x-1,-1,-1):
                id = self.id_order[i]
                for j in range(x,n):
                    if self.connecting(id,self.id_order[j]):
                        while j > x:
                            self.id_order[j],self.id_order[j-1] =self.id_order[j-1],self.id_order[j] 
                            j -= 1
                        break
                else:
                    continue
                break

    def init(self):
        self.node_surf = self.engine.assetManager.get('Assets/web_node.asset',pygame.Surface)
        self.ofst = (-self.node_surf.width//2,-self.node_surf.height//2)
        self.font = pygame.font.SysFont('Arial',16)
        self.ntosurf = Text.Mapping[int](self.font,True,'black')
        
    def onEngineEvent(self, event):
        if event == EngineEvent.STARTED:
            self.onStart()

    def onStart(self):
        pass
    
    def stepSim(self):
        accel = np.zeros((self.world.size,2))
        spring_k = 0.9
        for edge in self.gs.edges:
            a_node_i = self.world.getInd(edge.a_node)
            b_node_i = self.world.getInd(edge.b_node)
            
            dif = self.world.pos[a_node_i] - self.world.pos[b_node_i]
            
            length = np.sqrt(np.sum(dif*dif))
            norm = dif / length
            accel[a_node_i] -= norm * length * spring_k
            accel[b_node_i] += norm * length * spring_k
        
        for i in range(self.world.size):
            difs = self.world.pos[i] - self.world.getPoss()
            
            dists = np.sqrt(np.sum(difs*difs,axis=1))
            f_mags = 200 / (1+(dists/30))
            norms = (difs / dists[:,np.newaxis])
            # print(norms.shape)
            norms[np.logical_not(np.isfinite(norms))] = 0
            accel -= norms * f_mags[:,np.newaxis]
            
            # for j in range(i+1,self.world.size,1):
            #     dif = self.world.pos[i] - self.world.pos[j]
            #     distance = np.sqrt(np.sum(dif*dif))
            #     #convert distance to magnitude of force 
            #     f_mag = 200 / (1+distance/30)
            #     norm = dif / distance
            #     accel[i] += norm * f_mag
            #     accel[j] -= norm * f_mag
        accel -= self.world.getVels() * 2
        self.world.update(accel)
        

    def update(self):
        # self.sim_time_left -= self.world.dt
        keysd = self.engine.keys_down#pygame.key.get_just_pressed()
        keys = self.engine.keys
        if keysd[pygame.K_SPACE]:
            state,(start,end,tick,path) = self.gs_gen.__next__() # next(self.gs_gen)
            state.start_node = start
            state.end_node = end
            state.start_tick = tick
            self.setState(state,0,path)
        
        if keysd[pygame.K_c]:
            with debug.Timer() as tmr:
                crosses = self.getNumCross()
            print('Crosses:',crosses, f'in {tmr.format()}')
            
        if keysd[pygame.K_e]:
            print(self.connections)
        if keysd[pygame.K_o]:
            print('ID Order:',self.id_order)
        with debug.Timer() as tmr:
            self.stepSim()
        self.sim_cpu_time += tmr.time

    def draw(self):
        try:
            camera_offset = self.engine.getSystem(Camera).offset
        except LookupError:
            camera_offset = (0,0)
        poss = self.world.getPoss().copy() + camera_offset 
        for edge in self.gs.edges:
            self.engine.draw(Drawable.Line('white',poss[edge.a_node],poss[edge.b_node],3),layer=1)
        poss = poss + self.ofst
        # for edge in self.gs.edges:
        #     a_pos = self.ind_to_pos[self.id_order.index(edge.a_node)]
        #     b_pos = self.ind_to_pos[self.id_order.index(edge.b_node)]
        #     size = a_pos - b_pos
        #     rect =pygame.Rect(0,0,abs(size),abs(size))
        #     rect.centerx = (a_pos+b_pos)/2
        #     rect.centery = 0
        #     self.engine.draw(Drawable.Arc('white',rect.move(camera_offset),0,math.pi),layer=1)
        
        # self.engine.draw(Drawable.Lines('red',False,self.world.pos[self.path]+camera_offset,2),layer=1)
        self.engine.draw(Drawable.FBlits([(self.node_surf,pos) for pos in poss]),layer=2)
        
        
        for pos, id in zip(poss + (5,0),self.world.getIDs(),strict=True):
            self.engine.draw(Drawable.Blit(self.ntosurf[id],pos),layer=2)

