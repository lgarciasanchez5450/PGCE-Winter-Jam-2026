import zlib
import math
import debug

class Node:
    freeze_time:int
    explosion_time:int
    teleport_to:int

    def __init__(self):
        self.freeze_time = 0
        self.explosion_time = -1
        self.teleport_to = -1
    
    def __repr__(self):
        return f'N(FR:{self.freeze_time}, EX:{self.explosion_time}, TE:{self.teleport_to})'
    
class Edge:
    a_node:int
    b_node:int
    cycle:list[bool]

    def __init__(self, a_node=-1, b_node=-1, cycle=[True]):
        self.a_node = a_node
        self.b_node = b_node
        self.cycle = cycle
    
    def __repr__(self):
        return f'E({self.a_node}, {self.b_node}, {list(map(int,self.cycle))})'
    
class GameState:
    nodes:list[Node]
    edges:list[Edge]

    @property
    def start_node(self):
        return 0
    
    @property
    def end_node(self):
        return len(self.nodes) - 1

    def __init__(self):
        self.edges = []
        self.nodes = []
    
    def __repr__(self):
        return f'''
            start:{self.start_node}
            end:{self.end_node}
            nodes:{[f'{i}:{n}' for i,n in enumerate(self.nodes)]}
            edges:{self.edges}   
                '''

class GameStateGenerationParameters:
    N_NODE = 0
    FR_NODE = 1
    EX_NODE = 2
    TP_NODE = 3
    N_EDGE = 4
    C_EDGE = 5

    @property
    def total_nodes(self):
        return sum(self.node_amounts_remaining.values())

    node_amounts_remaining:dict[int, int]
    edge_amounts_remaining:dict[int, int]

    branch_chance:float

def defaultGameStateParameters() -> GameStateGenerationParameters:
    game_state_paramters: GameStateGenerationParameters = GameStateGenerationParameters()
    game_state_paramters.node_amounts_remaining = {GameStateGenerationParameters.FR_NODE: 0,
                                                    GameStateGenerationParameters.EX_NODE: 0,
                                                    GameStateGenerationParameters.TP_NODE: 0,
                                                    GameStateGenerationParameters.N_NODE: 3}
    game_state_paramters.edge_amounts_remaining = {GameStateGenerationParameters.C_EDGE: 0,
                                                   GameStateGenerationParameters.N_EDGE: 3}
    game_state_paramters.branch_chance = 0.75
    return game_state_paramters

import random
def generateSolvableGameState(p:GameStateGenerationParameters) -> GameState:
    solvable_game_state = GameState()

    def isRemainingDictEmpty(remaining:dict):
        return not any(remaining.values())

    def chooseRemainingType(remaining:dict) -> int:
        if isRemainingDictEmpty(remaining):
            return -1

        chosenType = random.choice(list(remaining.keys()))
        while remaining[chosenType] == 0:
            chosenType = random.choice(list(remaining.keys()))

        remaining[chosenType] -= 1
        return chosenType
    
    def isValidNodePos(pos:int):
        return pos < len(solvable_game_state.nodes)
    
    def generateEdgeBetween(node_pos_a:int, node_pos_b:int, tick:int):
        new_edge = Edge()

        if node_pos_a > node_pos_b:
            node_pos_a, node_pos_b = node_pos_b, node_pos_a

        new_edge.a_node = node_pos_a
        new_edge.b_node = node_pos_b

        new_edge_type = chooseRemainingType(p.edge_amounts_remaining)

        if new_edge_type == GameStateGenerationParameters.C_EDGE:
            new_edge.cycle = [False, False]
            new_edge.cycle[tick % 2] = True
        else:
            new_edge.cycle = [True]

        solvable_game_state.edges.append(new_edge)

    def step_once(tick:int,prev_pos:int,curr_pos:int) -> None:
        if isRemainingDictEmpty(p.node_amounts_remaining) or isRemainingDictEmpty(p.edge_amounts_remaining):
            return

        if not isValidNodePos(prev_pos):
            new_node:Node = Node()
            new_node_type = chooseRemainingType(p.node_amounts_remaining)

            if new_node_type == GameStateGenerationParameters.FR_NODE:
                new_node.freeze_time = 1
                tick += 1
            elif new_node_type == GameStateGenerationParameters.EX_NODE:
                new_node.explosion_time = tick + 1
            elif new_node_type == GameStateGenerationParameters.TP_NODE:
                new_node.teleport_to = curr_pos

            solvable_game_state.nodes.append(new_node)

            if new_node_type != GameStateGenerationParameters.TP_NODE:
                generateEdgeBetween(prev_pos,curr_pos,tick)
        
        if isValidNodePos(curr_pos):
            curr_node = solvable_game_state.nodes[curr_pos]
            
            tick += curr_node.freeze_time

            attempts_at_finding_non_teleporting_node = 1
            while curr_node.teleport_to != -1: # beware of infinite tp-node loops
                if attempts_at_finding_non_teleporting_node == len(solvable_game_state.nodes):
                    generateEdgeBetween(curr_pos,curr_node.teleport_to,tick) # TICK MIGHT NEED TO BE +1 or -1 here
                    curr_node.teleport_to = -1
                    step_once(tick,curr_pos,len(solvable_game_state.nodes)) #TICK IS NOT +1 HERE ON PURPOSE!!
                    return
                curr_node = solvable_game_state.nodes[curr_node.teleport_to]
                attempts_at_finding_non_teleporting_node += 1

        print("step_once called for tick:",tick)
        print(f'{prev_pos=}')
        print(f'{curr_pos=}')

        shouldBranch = isValidNodePos(curr_pos) or random.random() < p.branch_chance
        if shouldBranch:
            step_once(tick+1,curr_pos,len(solvable_game_state.nodes)+1)
        else:
            next_pos = random.randint(0,len(solvable_game_state.nodes)-1)
            attempts_at_finding_non_exploding_node = 1
            while solvable_game_state.nodes[next_pos].explosion_time != -1 and next_pos != curr_pos:
                if attempts_at_finding_non_exploding_node == len(solvable_game_state.nodes):
                    step_once(tick+1,curr_pos,len(solvable_game_state.nodes))
                    return
                next_pos = random.randint(0,len(solvable_game_state.nodes)-1)
                attempts_at_finding_non_exploding_node += 1
            
            step_once(tick+1,curr_pos,next_pos)

    solvable_game_state.nodes.append(Node())
    solvable_game_state.edges.append(Edge(0, 1))
    step_once(0,0,1)
    return solvable_game_state

def solve(g_state:GameState,max_depth:int):
    path = [-1]*(max_depth+1)
    best_path = [-1]*(max_depth+1)
    _solve(g_state,0,0,path,best_path,max_depth)
    return best_path

def _solve(g_state:GameState,tick:int,i:int,path:list[int],best_path:list[int],n:int):
    cur_pos = path[i]
    if cur_pos == g_state.end_node: return 0
    if i+1 > len(best_path): return -1
    if n <= 0: return -1
    cur_node = g_state.nodes[cur_pos]

    print(f"{path=}")

    if cur_node.explosion_time >= 0 and cur_node.explosion_time <= tick:
        return -1
    
    while cur_node.teleport_to != -1:
        cur_node = g_state.nodes[cur_node.teleport_to]        
        if cur_node.explosion_time >= 0 and cur_node.explosion_time <= tick:
            return -1 

    min_len = -1
    tick += cur_node.freeze_time
    for edge in g_state.edges:
        if not edge.cycle[tick%len(edge.cycle)]: continue
        go = False
        if cur_pos == edge.a_node:
            path[i+1] = edge.b_node
            go = True
        elif cur_pos == edge.b_node:
            path[i+1] = edge.a_node
            go = True
        if go:
            length_of_path = _solve(g_state,tick+1,i+1,path,best_path,n-1) + 1
            if length_of_path:
                min_len = length_of_path
                print("FOUND PATH")
                if i+length_of_path+1 < len(best_path):
                    best_path[:] = path[:i+length_of_path+1]
    return min_len

def generateInterestingGameStates(min_sol_length:int, game_state_paramters_func):
    game_state_paramters:GameStateGenerationParameters = game_state_paramters_func()
    total_nodes = game_state_paramters.total_nodes
    curr_game_state:GameState = generateSolvableGameState(game_state_paramters)
    shortest_path = solve(curr_game_state, total_nodes)
    if len(shortest_path) < min_sol_length:
        yield from generateInterestingGameStates(min_sol_length, game_state_paramters_func)
    else:
        yield curr_game_state, shortest_path
        yield from generateInterestingGameStates(min_sol_length, game_state_paramters_func)

if __name__ == '__main__':
    for gameState, solution in generateInterestingGameStates(0, defaultGameStateParameters):
        print(gameState)
        print(solution)
        input("Press enter to regenerate")