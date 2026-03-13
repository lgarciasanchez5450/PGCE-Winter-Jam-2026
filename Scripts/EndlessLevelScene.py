from pygame import Surface

from Engine.Asset.Manager import AssetManager
from Scripts.LevelScene import LevelScene
from gameSim import generateInterestingGameStates,buildGameStateParametersFunc
from game import Game

class LevelSceneEndless(LevelScene):
    def __init__(self, viewport: Surface, assets: AssetManager, game_state: Game):
        super().__init__(viewport, assets, game_state)
        self.state_m = game_state

        match self.state_m.endless_difficulty:
            case "easy":
                f = buildGameStateParametersFunc(0, 1, 0, 1, 0, 1, 3, 5, 3, 5, 2, 3, 0.25, 0.75)
                self.level_gen = generateInterestingGameStates(3,f)
            case "medium":
                f = buildGameStateParametersFunc(0, 3, 0, 3, 0, 3, 6, 8, 4, 6, 3, 5, 0.25, 0.75)
                self.level_gen = generateInterestingGameStates(5,f)
            case "hard":
                f = buildGameStateParametersFunc(0, 5, 0, 5, 0, 5, 7, 10, 6, 8, 4, 6, 0.25, 0.75)
                self.level_gen = generateInterestingGameStates(7,f)
        
    def onWin(self):
        # GENERATE NEW LEVEL. CAN USE self.state_m.endless_difficulty 
        # WILL DO TY LEO! - CAI
        
        self.setup(next(self.level_gen)[0])
        self.Start()
        