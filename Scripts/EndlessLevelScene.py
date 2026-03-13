from pygame import Surface

from Engine.Asset.Manager import AssetManager
from Scripts.LevelScene import LevelScene
from game import Game

class LevelSceneEndless(LevelScene):
    def __init__(self, viewport: Surface, assets: AssetManager, game_state: Game):
        super().__init__(viewport, assets, game_state)
        self.state_m = game_state
        
    def onWin(self):
        # GENERATE NEW LEVEL. CAN USE self.state_m.endless_difficulty 
        pass