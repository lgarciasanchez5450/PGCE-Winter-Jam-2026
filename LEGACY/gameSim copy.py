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



def solve(g_state:GameState,max_steps:int):
    shortest_path:list[int] = [-1]*(max_steps+1)

    start_path:list[int] = [g_state.start_node]

    def nextNodeOptions(g_state:GameState,tick:int,node:int):
        for edge in g_state.edges:
            if not edge.cycle[(g_state.start_tick + tick)%len(edge.cycle)]: continue
            if node == edge.a_node:
                yield edge.b_node
                
            if node == edge.b_node:
                yield edge.a_node

    def solveHelper(g_state:GameState,tick:int,curr_path:list[int]):
        curr_node = g_state.nodes[curr_path[-1]]

        if len(curr_path) > len(shortest_path): return
        if len(curr_path) > max_steps: return
        if curr_node.explosion_time > 0 and curr_node.explosion_time <= tick: return

        if curr_path[-1] == g_state.end_node:
            yield curr_path
        else:
            for option in nextNodeOptions(g_state, tick, curr_path[-1]):
                for solved_path in solveHelper(g_state, tick+1, curr_path + [option]):
                    yield solved_path

    for option in nextNodeOptions(g_state, g_state.start_tick, g_state.start_node):
        # print(f'{option=}')
        for solved_path in solveHelper(g_state, g_state.start_tick+1, start_path + [option]):
            shortest_path = min(shortest_path, solved_path, key=len)
    
    return shortest_path



state = GameState()
rng = random.Random(6)
state.nodes,state.edges = generateGraph(6,6,2,1,rng)
max_depth = 10
print(state.edges)
print(state.nodes)
solutions = []
for start_pos in range(len(state.nodes)):
    state.start_node = start_pos
    for end_pos in range(len(state.nodes)):
        state.end_node = end_pos
        if start_pos == end_pos: continue
        for tick in range(min(25,len(state.edges))):
            state.start_tick = tick
            
            if (short_path:=solve(state,max_depth)) != -1:
                solutions.append((start_pos,end_pos,tick,short_path))
                
solutions.sort(key=lambda x:len(x[3]),reverse=True)
for start_pos,end_pos,tick,path in solutions[:10]:
    print('start:',start_pos)
    print('end:',end_pos)
    print('start_tick:',tick)
    print(path)
    print('#####################')                
            
            
    
    
