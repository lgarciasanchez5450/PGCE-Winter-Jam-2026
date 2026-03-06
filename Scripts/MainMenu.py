from Engine import *
from Scripts.Camera import Camera
from Scripts.MapDrawer import MapDrawer
from Scripts.Level import Level
from gameSim import generateInterestingGameStates

class MainMenu(BaseSystem[()]):
    def getState(self) -> tuple[()]:
        return ()
    
    def setState(self):
        return
    
    def init(self):
        #transition to other state
        level_state = EngineState.empty()
        self.engine.addSystemToState(level_state,Camera,'',pygame.Vector2())
        self.engine.addSystemToState(level_state,MapDrawer,'',[],[])
        self.engine.addSystemToState(level_state,Level,'',next(generateInterestingGameStates(1,10,5,7,2,3,False))[0])
        self.engine.startCoroutine(self.EngineStateTransition(level_state))
        
    def EngineStateTransition(self,state:EngineState):
        if False: yield
        self.engine.clearState()
        self.engine.loadState(state)
        
    
