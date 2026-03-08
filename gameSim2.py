import zlib
import math
import debug

class Node:
    freeze_time:int
    explosion_time:int
    teleport_to:int
    
    def __repr__(self):
        return f'N(FR:{self.freeze_time}, EX:{self.explosion_time}, TE:{self.teleport_to})'
    
class Edge:
    a_node:int
    b_node:int
    cycle:list[bool]
    
    def __repr__(self):
        return f'E({self.a_node}, {self.b_node}, {list(map(int,self.cycle))})'
    
class GameState:
    nodes:list[Node]
    edges:list[Edge]

    def __init__(self):
        self.edges = []
        self.nodes = []
    
    def __repr__(self):
        return f'''
            start:{self.nodes[0]}
            end:{self.nodes[-1]}
            nodes:{[f'{i}:{n}' for i,n in enumerate(self.nodes)]}
            edges:{self.edges}   
                '''

class GameStateGenerationParameters:
    steps:int
    max_fr_nodes:int
    max_ex_nodes:int
    max_tp_nodes:int
    max_cycle_edges:int
    fr_node_weight:float
    ex_node_weight:float
    tp_node_weight:float
    cycle_edge_weight:float
    branch_factor:float

def defaultGameStateParameters() -> GameStateGenerationParameters:
    game_state_paramters: GameStateGenerationParameters = GameStateGenerationParameters()
    game_state_paramters.steps = 10
    game_state_paramters.max_fr_nodes = 3
    game_state_paramters.max_ex_nodes = 3
    game_state_paramters.max_tp_nodes = 3
    game_state_paramters.max_cycle_edges = 3
    game_state_paramters.fr_node_weight=1/4
    game_state_paramters.ex_node_weight=1/4
    game_state_paramters.tp_node_weight=1/4
    game_state_paramters.cycle_edge_weight=1/2
    game_state_paramters.branch_factor=1/3
    return game_state_paramters

import random
def generateSolvableGameState(p: GameStateGenerationParameters) -> GameState:
    solvable_game_state = GameState()
    nodeTypeResolution = 100
    nodeTypeRelativeFrequency = ["fr" for _ in range(int(p.fr_node_weight*nodeTypeResolution))]
    nodeTypeRelativeFrequency += ["ex" for _ in range(int(p.ex_node_weight*nodeTypeResolution))]
    nodeTypeRelativeFrequency += ["tp" for _ in range(int(p.tp_node_weight*nodeTypeResolution))]
    nodeTypeRelativeFrequency += ["n" for _ in range(int((1-p.fr_node_weight-p.ex_node_weight-p.tp_node_weight)*nodeTypeResolution))]

    def step_once(steps_remaining:int,fr_nodes_remaining:int,ex_nodes_remaining:int,tp_nodes_remaining:int,cycle_edges_remaining:int,returnedDuringLastStep:bool) -> None:
        if steps_remaining == 0:
            return

        shouldBranch = returnedDuringLastStep or random.random() >= p.branch_factor 
        if shouldBranch:
            nodesOfTypeRemaining = False
            nodeTypeToUse = "n"
            while not nodesOfTypeRemaining:
                nodeTypeToUse = random.choice(nodeTypeRelativeFrequency)
                if nodeTypeToUse == "fr": nodesOfTypeRemaining = fr_nodes_remaining > 0
                if nodeTypeToUse == "ex": nodesOfTypeRemaining = ex_nodes_remaining > 0
                if nodeTypeToUse == "tp": nodesOfTypeRemaining = tp_nodes_remaining > 0
                if nodeTypeToUse == "n": nodesOfTypeRemaining = True

            new_node:Node = Node()

            if nodeTypeToUse == "fr" or nodeTypeToUse == "ex" or nodeTypeToUse == "n":
                if len(solvable_game_state.nodes) > 0:
                    edge:Edge = Edge()
                    edge.a_node = len(solvable_game_state.nodes) - 1
                    edge.b_node = len(solvable_game_state.nodes)
                    edge.cycle = [True]

                    shouldCreateCycleEdge = cycle_edges_remaining > 0 and random.random() <= p.cycle_edge_weight
                    if shouldCreateCycleEdge:
                        edge.cycle = [False, False]
                        isOddTick:int = (p.steps-steps_remaining) % 2
                        edge.cycle[isOddTick] = True

            new_node.freeze_time = -1
            new_node.explosion_time = -1
            new_node.teleport_to = -1

            if nodeTypeToUse == "fr":
                new_node.freeze_time = 100 # choose some number of freeze time, might affect something be careful
            elif nodeTypeToUse == "ex":
                new_node.explosion_time = 100 # can be current tick + 1 - any number

            if nodeTypeToUse == "t":
                new_node.teleport_to

            solvable_game_state.nodes.append(new_node)

    step_once(p.steps,p.max_fr_nodes,p.max_ex_nodes,p.max_tp_nodes,p.max_cycle_edges,True)
    return solvable_game_state


def solveGameStateInMinimumMoves(gameState:GameState) -> tuple[int, list[int]]:
    return -1, [0]

def generateInterestingGameStates(min_sol_length:int, game_state_paramters: GameStateGenerationParameters):
    while True:
        curr_game_state:GameState = generateSolvableGameState(game_state_paramters)
        min_moves_required, shortest_path = solveGameStateInMinimumMoves(curr_game_state)
        while min_moves_required < min_sol_length:
            curr_game_state = generateSolvableGameState(game_state_paramters)

        yield curr_game_state, shortest_path

if __name__ == '__main__':
    for gameState, solution in generateInterestingGameStates(3, defaultGameStateParameters()):
        print(gameState)
        print(solution)
        input("Press enter to regenerate")