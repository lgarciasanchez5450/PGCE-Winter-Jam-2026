import debug
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

@debug.profile
def generateGraph(n:int,e:int,e_cycle_max:int,max_cycle_edges:int,rng:random.Random) -> tuple[list[Node],list[Edge]]:
    if e<n-1: print('Bad!');raise Exception
    nodes = []
    for i in range(n):
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
    for i in range(e):
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
        if i < max_cycle_edges:
            edge.cycle = [rng.random() < 0.5 for _ in range(e_cycle_max)]
        else:
            edge.cycle = [True]
        edges.append(edge)
        
    return nodes,edges
  

def solve(g_state:GameState,tick:int,path:list[int],best_path:list[int],n:int):
    cur_pos = path[tick]
    if cur_pos == g_state.end_node: return 0
    if tick+1 > len(best_path): return -1
    if n <= 0: return -1
    cur_node = g_state.nodes[cur_pos]
    if cur_node.explosion_time > 0 and cur_node.explosion_time <= tick:
        return -1
    min_len=-1
    for edge in g_state.edges:
        if not edge.cycle[(g_state.start_tick + tick)%len(edge.cycle)]: continue
        go = False
        if cur_pos == edge.a_node:
            path[tick+1] = edge.b_node
            go = True
        elif cur_pos == edge.b_node:
            path[tick+1] = edge.a_node
            go = True
        if go:
            length_of_path = solve(g_state,tick+1,path,best_path,n-1) + 1
            if length_of_path:
                min_len = length_of_path
                if tick+length_of_path+1 < len(best_path):
                    best_path[:] = path[:tick+length_of_path+1]
    return min_len

state = GameState()
rng = random.Random(6)
state.nodes,state.edges = generateGraph(6,6,2,1,rng)
max_depth = 10
path = [-1]*(max_depth+1)
print(state.edges)
print(state.nodes)
solutions = []
variations = 0
with debug.Timer() as tmr:
    for start_pos in range(len(state.nodes)):
        state.start_node = start_pos
        for end_pos in range(len(state.nodes)):
            state.end_node = end_pos
            if start_pos == end_pos: continue
            for tick in range(min(25,len(state.edges))):
                state.start_tick = tick
                path[0] = start_pos
                best_path = [-1]*(max_depth+1)
                variations += 1
                if (len_path:=solve(state,0,path,best_path,max_depth)) != -1:
                    solutions.append((start_pos,end_pos,tick,best_path.copy()))
       

print(f'{variations=} in {tmr.format()}')                
solutions.sort(key=lambda x:len(x[3]),reverse=True)
for start_pos,end_pos,tick,path in solutions[:10]:
    print('start:',start_pos)
    print('end:',end_pos)
    print('tick:',tick)
    print(path)
    print('#####################')                
            
            
    
    
