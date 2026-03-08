from Engine import *

from gameSim import GameState, defaultGameStateParameters, generateInterestingGameStates

class Level:
    game_state:GameState
    completed:bool

class GameData(BaseSystem[()]):

    def getState(self) -> tuple[()]:
        return ()
    
    def setState(self):
        self.volume = 1
        self.levels:list[Level] = []
        
        gen = generateInterestingGameStates(2, defaultGameStateParameters)
        LEVELS = 30
        for _ in range(LEVELS):
            level = Level()
            level.completed = False
            level.game_state = next(gen)[0]
            self.levels.append(level)
            
        