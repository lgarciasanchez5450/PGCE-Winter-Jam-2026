from Engine import *
from Engine import Engine
from gameSim import Node,Edge
from Engine.VerletPhysics import VerletPhysics
from Scripts.Camera import Camera
import numpy as np
from Scripts.Map import Map as _

def sort(id_order:list[int],connections:set[tuple[int,int]]):
    def connect(a,b):
        if b<a: a,b = b,a
        return (a,b) in connections

    n = len(id_order)
    for x in range(n):
        for i in range(x-1,-1,-1):
            id = id_order[i]
            for j in range(x,n):
                if connect(id,id_order[j]):
                    while j > x:
                        id_order[j],id_order[j-1] =id_order[j-1],id_order[j] 
                        j -= 1
                    break
            else:
                continue
            break
        
class MapDrawer(BaseSystem[list[Node],list[Edge]]):
    def getState(self) -> tuple[list[Node], list[Edge]]:
        return self.nodes.copy(),self.edges.copy()

    def setState(self,nodes:list[Node],edges:list[Edge]):
        self.setMap(nodes,edges)

    def applyChanges(self):
        self.world.clear()
        width = max(300,20*len(self.nodes))
        self.ind_to_pos = np.linspace(-width//2,width//2,len(self.nodes))
        id_order = list(range(len(self.nodes)))
        connections:set[tuple[int,int]] = set()
        for edge in self.edges:
            connections.add((edge.a_node,edge.b_node))
        sort(id_order,connections)
        len_nodes = len(self.nodes)
        r = 100
        theta_offset = np.pi / 2
        for i in range(len_nodes):
            id = id_order[i]
            theta = (id*2*np.pi +theta_offset)/ len_nodes
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            self.world.append((x,y),(0,0))
    
    def setMap(self,nodes:list[Node],edges:list[Edge]):
        self.nodes = nodes
        self.edges = edges
        self.initialized = False

    def init(self):
        self.world = VerletPhysics(0,0.1)
        self.node_surf = self.engine.assetManager.get('Assets/web_node.asset',pygame.Surface)
        self.font = pygame.font.SysFont('Arial',16)
        self.ntosurf = Text.Mapping[int](self.font,True,'black')

    def getPos(self,node:int):
        return self.world.get(node)
        
    def update(self):
        if not self.initialized:
            self.applyChanges()
            self.initialized = True    
        accel = np.zeros((self.world.size,2))
        spring_k = 0.9
        for edge in self.edges:
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
            norms[np.logical_not(np.isfinite(norms))] = 0
            accel -= norms * f_mags[:,np.newaxis]
        accel -= self.world.getVels() * 2
        self.world.update(accel)
    
    def draw(self):
        try:
            camera_offset = self.engine.getSystem(Camera).offset
        except LookupError:
            camera_offset = (0,0)
        poss = self.world.getPoss().copy() + camera_offset 
        for edge in self.edges:
            self.engine.draw(Drawable.Line('white',poss[edge.a_node],poss[edge.b_node],3),layer=1)
        poss = poss + (-self.node_surf.width//2,-self.node_surf.height//2)   
        self.engine.draw(Drawable.FBlits([(self.node_surf,pos) for pos in poss]),layer=2)
        
        for pos, id in zip(poss + (5,0),self.world.getIDs(),strict=True):
            self.engine.draw(Drawable.Blit(self.ntosurf[id],pos),layer=2)
