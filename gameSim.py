class Node:
    freeze_time:int
    explosion_time:int
    def copy(self):
        out = Node()
        out.freeze_time = self.freeze_time
        out.explosion_time = self.explosion_time
        return out
    
    def __repr__(self):
        return f'N({self.freeze_time}, {self.explosion_time})'
    
class Edge:
    a_node:int
    b_node:int
    cycle:list[bool]
    
    def copy(self):
        out = Edge()
        out.a_node = self.a_node
        out.b_node = self.b_node
        out.cycle = self.cycle.copy()
        return out
    
    def __repr__(self):
        return f'E({self.a_node}, {self.b_node}, {list(map(int,self.cycle))})'
    
class GameState:
    start_node:int
    end_node:int
    nodes:list[Node]
    edges:list[Edge]
    start_tick:int
    def __init__(self):
        self.edges = []
        self.nodes = []
    
    def copy(self):
        out = GameState()
        out.start_node = self.start_node
        out.end_node = self.end_node
        out.nodes = [n.copy() for n in self.nodes]
        out.edges = [n.copy() for n in self.edges]
        return out
    
    def __repr__(self):
        return f'''
start:{self.start_node}
end:{self.end_node}
nodes:{self.nodes}
edges:{self.edges}
tick:{self.start_tick}    
    '''
    
    
import random


def generateGraph(n:int,e:int,e_cycle_max:int,rng:random.Random) -> tuple[list[Node],list[Edge]]:
    if e<n-1: print('Bad!');raise Exception
    nodes = []
    for _ in range(n):
        node = Node()
        if rng.randint(0,1):
            node.freeze_time = -1
            node.explosion_time = rng.randint(0,e)
        else:
            node.freeze_time = rng.randint(0,e)
            node.explosion_time = -1
            
        nodes.append(node)

    connected:set[tuple[int,int]] = set()
    edges = []
    for _ in range(e):
        while True:
            a = rng.randint(0,n-1)
            b = rng.randint(0,n-1)
            while b == a:
                b = rng.randint(0,n-1)
            if b<a:
                a,b = b,a
            if (a,b) not in connected:
                connected.add((a,b))
                break
        edge = Edge()
        edge.a_node = a
        edge.b_node = b
        edge.cycle = [rng.random() < 0.5 for _ in range(e_cycle_max)]
        edges.append(edge)
        
    return nodes,edges
       
def solve(g_state:GameState,tick:int,path:list[int],n:int):
    if g_state.start_node == g_state.end_node: return True
    if n <= 0: return False
    cur_pos = path[tick]
    cur_node = g_state.nodes[cur_pos]
    if cur_node.explosion_time > 0 and cur_node.explosion_time <= tick:
        return False
    
    for edge in g_state.edges:
        if not edge.cycle[g_state.start_tick + tick]: continue
        if cur_pos == edge.a_node:
            path[tick+1] = edge.b_node
            if solve(g_state,tick+1,path,n-1):
                return True
        if cur_pos == edge.b_node:
            path[tick+1] = edge.a_node
            if solve(g_state,tick+1,path,n-1):
                return True
    return False
    

state = GameState()
rng = random.Random(5)
state.nodes,state.edges = generateGraph(10,10,5,rng)
max_depth = 10
path = [-1]*max_depth
for start_pos in range(len(state.nodes)):
    for end_pos in range(len(state.nodes)):
        if start_pos == end_pos: continue
        for tick in range(25):
            state.start_tick = tick
            state.start_node = start_pos
            state.end_node = end_pos
            if solve(state,0,path,max_depth):
                print(state)
            
            
    
    
