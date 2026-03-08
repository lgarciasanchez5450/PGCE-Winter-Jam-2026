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
            start:{self.nodes[0]}
            end:{self.nodes[-1]}
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

    node_amounts_remaining:dict[int, int]
    edge_amounts_remaining:dict[int, int]

    branch_chance:float

def defaultGameStateParameters() -> GameStateGenerationParameters:
    game_state_paramters: GameStateGenerationParameters = GameStateGenerationParameters()
    game_state_paramters.node_amounts_remaining = {GameStateGenerationParameters.FR_NODE: 3,
                                                    GameStateGenerationParameters.EX_NODE: 3,
                                                    GameStateGenerationParameters.TP_NODE: 3,
                                                    GameStateGenerationParameters.N_NODE: 5}
    game_state_paramters.edge_amounts_remaining = {GameStateGenerationParameters.C_EDGE: 3,
                                                   GameStateGenerationParameters.N_EDGE: 5}
    game_state_paramters.branch_chance = 0.25
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

    def step_once(tick:int,prev_pos:int,curr_pos:int) -> None:
        if isRemainingDictEmpty(p.node_amounts_remaining) or isRemainingDictEmpty(p.edge_amounts_remaining):
            return

        # if prev_pos is not an index in nodes, make and determine that node
        if prev_pos >= len(solvable_game_state.nodes):
            pass

        # take next step

    step_once(0,0,1)
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