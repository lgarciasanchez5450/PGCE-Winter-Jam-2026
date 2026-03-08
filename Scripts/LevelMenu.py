from Engine import *
from Scripts.GameData import GameData,Level
from Scripts.Level import LevelSystem
import time

class LevelsDrawer:
    def __init__(self,levels_menu:'LevelMenu') -> None:
        self.menu = levels_menu
        self.font = self.menu.engine.assetManager.get('EditorAssets/default_font.asset',pygame.Font)
        self.text = Text.Mapping[int](self.font,True,'black')
        
    def draw(self,surf:pygame.Surface):
        rect = surf.get_rect()
        
        rect.inflate_ip(-100,-100)        
        pygame.draw.rect(surf,(100,200,100),rect,0,10)
        
        
        grid_w = self.menu.grid_w
        padding = 10
        level_width = 50
        level_height = 50
        total_width = rect.width
        spacing = (total_width - 2*padding - grid_w*level_width)/(grid_w-1)
        #total_width = 2*padding + grid_w*level_width+(grid_w-1)*spacing
        
        
        for i,level in enumerate(self.menu.game.levels):
            x = i % grid_w
            y = i // grid_w

            offset_x = int(x * level_width + x*spacing) + padding
            offset_y = int(y * level_height + y*spacing) + padding
            r = pygame.Rect(rect.left+offset_x,rect.top+ offset_y,level_width,level_height)
            
            self.drawLevel(surf,i,level,r,i==self.menu.current_level_i)
            
    def drawLevel(self,surf:pygame.Surface,num:int,level:Level,r:pygame.Rect,selected:bool):
        if level.completed:
            pygame.draw.rect(surf,'dark green',r,0,4)
        else:
            pygame.draw.rect(surf,'dark gray',r,0,4)
        if selected:
            pygame.draw.rect(surf,'gold',r,3,4)
        else:
            pygame.draw.rect(surf,'gray',r,3,4)
            
        
        s = self.text[num+1]
        surf.blit(s,s.get_rect(center=r.center))
        


class LevelMenu(BaseSystem[()]):
    def setState(self):
        print('Setting Level Menyu State')
        pass
    
    
    def getState(self):
        return ()
    
    def init(self):
        self.game = self.engine.getSystem(GameData)
        self.current_level_i = 0
        self.grid_w = 7
        self.renderer = LevelsDrawer(self)
        print("INITIALIZEZD LEVEL MENU!")
        
        
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

        
        
    def update(self):
        if self.engine.keys_down[pygame.K_z]:
            scene = self.engine.getScene('level')
            scene.setSystemArgs(LevelSystem,'',False,self.game.levels[self.current_level_i].game_state)
            self.engine.startCoroutine(self.EngineStateTransition(scene))
        dy = self.engine.keys_down[pygame.K_DOWN] - self.engine.keys_down[pygame.K_UP]
        dx = self.engine.keys_down[pygame.K_RIGHT] - self.engine.keys_down[pygame.K_LEFT]
        
        di = dx + dy * self.grid_w
        
        self.current_level_i += di
        self.current_level_i = min(max(self.current_level_i,0),len(self.game.levels)-1)
        # print(self.current_level_i)
    
    def draw(self):
        self.engine.draw(self.renderer)