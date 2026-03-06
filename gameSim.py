import zlib
import math
import debug

class Node:
    freeze_time:int
    explosion_time:int
    
    def __repr__(self):
        return f'N({self.freeze_time}, {self.explosion_time})'
    
class Edge:
    a_node:int
    b_node:int
    cycle:list[bool]
    
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
    
    def __repr__(self):
        return f'''
start:{self.start_node}
end:{self.end_node}
nodes:{[f'{i}:{n}' for i,n in enumerate(self.nodes)]}
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
            node.explosion_time = rng.randint(2,e)
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

        while not any(edge.cycle) or (all(edge.cycle) and len(edge.cycle) > 1):
            edge.cycle = [rng.random() < 0.5 for _ in range(e_cycle_max)]

        edges.append(edge)
    return nodes,edges


def solve(g_state:GameState,tick:int,i:int,path:list[int],best_path:list[int],n:int):
    cur_pos = path[i]
    if cur_pos == g_state.end_node: return 0
    if i+1 > len(best_path): return -1
    if n <= 0: return -1
    cur_node = g_state.nodes[cur_pos]
    if cur_node.explosion_time >= 0 and cur_node.explosion_time <= tick:
        return -1
    min_len=-1
    tick +=  cur_node.freeze_time
    for edge in g_state.edges:
        if not edge.cycle[(g_state.start_tick + tick)%len(edge.cycle)]: continue
        go = False
        if cur_pos == edge.a_node:
            path[i+1] = edge.b_node
            go = True
        elif cur_pos == edge.b_node:
            path[i+1] = edge.a_node
            go = True
        if go:
            length_of_path = solve(g_state,tick+1,i+1,path,best_path,n-1) + 1
            if length_of_path:
                min_len = length_of_path
                if i+length_of_path+1 < len(best_path):
                    best_path[:] = path[:i+length_of_path+1]
    return min_len

def solutionUsesAllCycles(g_state:GameState,path:list[int]):
    # for each edge that cycles, the solution must include that pair of nodes as adjacent numbers (in any order)
    edges_that_cycle = [edge for edge in g_state.edges if not all(edge.cycle)] # if edge.cycle contains any 0s, the edge actually cycles
    
    for edge in edges_that_cycle:
        if not any([[edge.a_node, edge.b_node] == sorted(path[i:i+2]) for i in range(len(path)-1)]):
            return False
    return True

def filterSolutionsForAllCycleUse(state:GameState,solutions:list):
    solution_blacklist = []
    for start_pos,end_pos,tick,path in solutions:
        if not solutionUsesAllCycles(state, path):
            solution_blacklist.append((start_pos, end_pos)) 
    
    new_solutions = [solution for solution in solutions if (solution[0], solution[1]) not in solution_blacklist]

    return new_solutions

def generateInterestingGameStates(min_solution_len:int,max_depth:int,n:int,e:int,e_cycle_max:int,max_cycle_edges:int,use_all_cycles:bool):
    master_rng = random.Random()
    while True:
        state = GameState()
        rng = random.Random(zlib.adler32(str(master_rng.random()).encode()))
        state.nodes,state.edges = generateGraph(n,e,e_cycle_max,max_cycle_edges,rng)
        path = [-1]*(max_depth+1)
        solutions = []
        variations = 0
        with debug.Timer() as tmr:
            for start_pos in range(len(state.nodes)):
                state.start_node = start_pos
                for end_pos in range(len(state.nodes)):
                    state.end_node = end_pos
                    if start_pos == end_pos: continue
                    for tick in range(min(25,e_cycle_max)):
                        state.start_tick = tick
                        path[0] = start_pos
                        best_path = [-1]*(max_depth+1)
                        variations += 1
                        if solve(state,0,0,path,best_path,max_depth) != -1:
                            solutions.append((start_pos,end_pos,tick,best_path.copy()))

        print(f'{variations=} in {tmr.format()}')                
        solutions.sort(key=lambda x:len(x[3]),reverse=True)
        
        if use_all_cycles:
            solutions = filterSolutionsForAllCycleUse(state, solutions)

        got:set[tuple[int,int]] = set()
        unique_start_end_solutions = []

        for start_pos,end_pos,tick,path in solutions:
            t = (start_pos,end_pos)
            if t in got: continue
            if len(path) < min_solution_len: continue
            got.add(t)
            unique_start_end_solutions.append((start_pos,end_pos,tick,path))
        print(f'[{", ".join([f'{i}:{n}' for i,n in enumerate(state.nodes)])}]')
        print(state.edges)
        for start_pos,end_pos,tick,path in unique_start_end_solutions:
            print('start:',start_pos)
            print('end:',end_pos)
            print('tick:',tick)
            print(path)
            print('#####################')

        if len(unique_start_end_solutions) > 0: 
            yield state, unique_start_end_solutions[0]
        
if __name__ == '__main__':
    nodes = 6
    edgePercent = 0.52

    edges = int(math.comb(nodes, 2) * edgePercent)

    max_cycle_edges = min(nodes, 3)

    for x in generateInterestingGameStates(5,20,nodes,edges,2,max_cycle_edges,True):
        input("Press enter to regenerate")

# make generateInterestingGameStates yield gamestate and path 