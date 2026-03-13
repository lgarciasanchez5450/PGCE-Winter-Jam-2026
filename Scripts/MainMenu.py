from Engine import *
from Engine import Scene
from Scripts.Camera import Camera
from Scripts.MapDrawer import MapDrawer
from Scripts.Level import LevelSystem
from gameSim import generateInterestingGameStates
import time

class MainMenu(BaseSystem[()]):
    def getState(self) -> tuple[()]:
        return ()
    
    def setState(self):
        return
    
    def init(self):
        self.font = self.engine.assets.get('EditorAssets/default_font.asset',pygame.Font)
        self.text = Text.Mapping[str](self.font,True,'white','gray')
        self.title_card = self.engine.assets.get('Resources/realTitleCard.png',pygame.Surface)
        self.title_card_rect = self.title_card.get_rect()
        self.transition_to_level_menu = False
        self.transition_to_settings = False
        
    def __init__(self, engine: Scene, name: str):
        super().__init__(engine, name)
        self.addHook(Events.KeyDown,self.onKeyDown)
        
    def onKeyDown(self,event:Events.KeyDown):
        if event.key == pygame.K_z:
            print("GOING TO LEVELS")
            self.transition_to_level_menu = True
            return True
        elif event.key == pygame.K_x:
            print("GOING TO SETTINGS")
            self.transition_to_settings = True
            return True
        return False

        
    # def update(self):
    #     if self.engine.keys_down[pygame.K_z]:
    #         self.transition_to_level_menu = True
    #     if self.engine.keys_down[pygame.K_x]:
    #         self.transition_to_settings = True
        
    def draw(self):
        surf_size = self.engine.screen.size
        self.title_card_rect.centerx = surf_size[0]//2
        self.title_card_rect.centery = surf_size[1]//2
        
        self.engine.draw(Drawable.Fill('purple'),layer = 10)
        
        self.engine.draw(Drawable.Blit(self.title_card,self.title_card_rect),layer=11)
        self.engine.draw(Drawable.Blit(self.text.get('Pres Z to play!'),self.title_card_rect.move(0,30)),layer=11)
        self.engine.draw(Drawable.Blit(self.text.get('X for settings'),self.title_card_rect.move(0,80)),layer=11)
        
    
        
    def EngineStateTransition(self,state:EngineState):
        t = time.perf_counter()
        t_end = t+1
        surf = pygame.Surface(self.engine.screen.size)
        while t < t_end:
            dif = t_end-t
            surf.set_alpha(int((1-dif)**2*255))
            self.engine.draw(Drawable.Blit(surf),layer=99)
            yield
            t = time.perf_counter()
        surf.set_alpha(255)        
        self.engine.draw(Drawable.Blit(surf),layer=99)
        self.engine.clearState()
        self.engine.loadState(state)
        self.engine.Initialize()
        t = time.perf_counter()
        t_end = t+1

        while t < t_end:
            dif = t_end-t
            surf.set_alpha(int((dif)**2*255))
            self.engine.draw(Drawable.Blit(surf),layer=99)
            yield
            t = time.perf_counter()
        surf.set_alpha(0)        
        self.engine.draw(Drawable.Blit(surf),layer=99)
