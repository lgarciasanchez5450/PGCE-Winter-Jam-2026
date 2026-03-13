from Engine import *
from Engine import Scene
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
        self.tick = 0

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
        self.constraints.clear()
        for i in range(1,len_nodes):
            self.constraints.append((0,i))
    
    def setMap(self,nodes:list[Node],edges:list[Edge]):
        self.nodes = nodes
        self.edges = edges
        self.initialized = False
        self.constraints:list[tuple[int,int]] = []


    def setTick(self,tick:int):
        self.tick = tick

    def init(self):
        self.world = VerletPhysics(0,0.1)
        self.node_surf = self.engine.assets.get('Assets/web_node.asset',pygame.Surface)
        self.node_surf_gray = self.node_surf.copy()
        self.node_surf_gray.set_alpha(100)
        self.font = pygame.font.SysFont('Arial',16)
        self.ntosurf = Text.Mapping[int](self.font,True,'black')
        self.text = Text.Text(self.font,True,'white')

    def getPos(self,node:int):
        return self.world.get(node)
        
    def update(self):
        if not self.initialized:
            self.applyChanges()
            self.initialized = True    
        accel = np.zeros((self.world.size,2))
        spring_k = 0.9
        edge_lengths:list[float] = []
        for edge in self.edges:
            a_node_i = self.world.getInd(edge.a_node)
            b_node_i = self.world.getInd(edge.b_node)
            dif = self.world.pos[a_node_i] - self.world.pos[b_node_i]
            distance = np.sqrt(np.sum(dif*dif))
            edge_lengths.append(distance)
            norm = dif / distance
            accel[a_node_i] -= norm * distance * spring_k
            accel[b_node_i] += norm * distance * spring_k
        edge_lengths.sort()
        length = sum(edge_lengths) / len(edge_lengths) * 0.05
        for b_node in range(len(self.nodes)):
            b_node_i = self.world.getInd(b_node)
            dif = self.world.pos[b_node_i]
            distance = np.sqrt(np.sum(dif*dif))
            force = distance/length
            norm = dif / distance
            accel[b_node_i] -= norm * force
            accel[b_node_i] -= (dif /length)
                    
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
        self.engine.draw(Drawable.BlitFuture(self.text.setText(f'Tick: {self.tick}').render),layer = 2)
        for edge in self.edges:
            if not all(edge.cycle):
                if not edge.cycle[(self.tick)%len(edge.cycle)]: 
                    self.engine.draw(Drawable.Line((50,50,50),poss[edge.a_node],poss[edge.b_node],3),layer=1)
                else:
                    self.engine.draw(Drawable.Line("deeppink3",poss[edge.a_node],poss[edge.b_node],3),layer=1)
            else:
                self.engine.draw(Drawable.Line('white',poss[edge.a_node],poss[edge.b_node],3),layer=1)
        poss = poss + (-self.node_surf.width//2,-self.node_surf.height//2)

        for node_i,node in enumerate(self.nodes):
            pos = poss[self.world.id_to_ind[node_i]]
            if node.explosion_time != -1:
                self.engine.draw(
                    Drawable.Rect('gold2',pygame.Rect(pos[0]-3,pos[1]-3,26,26),width=3),layer=3
                )
                if node.explosion_time <= self.tick:
                    self.engine.draw(Drawable.Blit(self.node_surf_gray,pos),layer=2)
                else:
                    self.engine.draw(Drawable.Blit(self.node_surf,pos),layer=2)
            else:
                self.engine.draw(Drawable.Blit(self.node_surf,pos),layer=2)
                
            if node.teleport_to != - 1:
                self.engine.draw(
                    Drawable.Rect('darkorchid1',pygame.Rect(pos[0]-3,pos[1]-3,26,26),width=3),layer=3
                )
            elif node.freeze_time != 0:
                self.engine.draw(
                    Drawable.Rect('dodgerblue2',pygame.Rect(pos[0]-3,pos[1]-3,26,26),width=3),layer=3
                )
                
        # self.engine.draw(Drawable.FBlits([(self.node_surf,pos) for pos in poss]),layer=2)
        
        for pos, id in zip(poss + (5,0),self.world.getIDs(),strict=True):
            self.engine.draw(Drawable.Blit(self.ntosurf[id],pos),layer=2)
