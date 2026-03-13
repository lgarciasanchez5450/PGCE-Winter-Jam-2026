from pygame import Surface, Event
from pygame.key import ScancodeWrapper
from Engine import UI as ui
from Engine import *
import typing
from Scripts.MainMenuScene import Button,LerpThing
from Scripts import easings
if typing.TYPE_CHECKING:
    from game import Game
    
def blit_at(to:Surface,source:Surface,rect:pygame.Rect,align_x:float=0.5,align_y:float=0.5):
    x = rect.left + int((rect.width-source.width) * align_x)
    y = rect.top + int((rect.height-source.height) * align_y)
    to.blit(source,(x,y))
    
class LevelSelect(Button):
    def __init__(self,title:str,desc:str,tr:Text.Mapping,size) -> None:
        super().__init__(tr,title,size)
        self.title = title
        self.desc = desc
        self.tr = tr
        
    def draw(self, surf: Surface):
        r = self.rect#.inflate(-10,-10)
        # pygame.draw.rect(surf,'white',r,2,5)
        blit_at(surf,self.tr[self.title],r)
        

class LevelMenu(Scene):
    def __init__(self, viewport: Surface, assets: AssetManager,game_state:'Game'):
        super().__init__(viewport, assets)
        self.state_m = game_state
        self.font = assets.get('./EditorAssets/default_font.asset',pygame.Font)

        self.tr = Text.Mapping[str](self.font,True,'white')
        self.createUI()
        
    def createUI(self):
        ystack = ui.YStack([0])
        self.button_back = Button(self.tr,'Back',size=(50,40))
        self.level1 = LevelSelect('Level 1','',self.tr,size=(80,40))
        self.level2 = LevelSelect('Level 2','',self.tr,size=(0,40))
        self.level3 = LevelSelect('Level 3','',self.tr,size=(0,40))
        self.level4 = LevelSelect('Level 4','',self.tr,size=(0,40))
        self.level5 = LevelSelect('Level 5','',self.tr,size=(0,40))
        self.level6 = LevelSelect('Level 6','',self.tr,size=(0,40))
        
        ystack.setChildren([
            self.level1,
            self.level2,
            self.level3,
            self.level4,
            self.level5,
            self.level6,
            self.button_back,
        ])
        
        self.ui = ui.Padding(ui.Place(ystack,x=0.5,y=0.5),[20,20,20],)
        self.selections:dict[Button,dict[int,Button]] = {
            self.level1:{pygame.K_DOWN:self.level2},
            self.level2:{pygame.K_UP:self.level1,pygame.K_DOWN:self.level3},
            self.level3:{pygame.K_UP:self.level2,pygame.K_DOWN:self.level4},
            self.level4:{pygame.K_UP:self.level3,pygame.K_DOWN:self.level5},
            self.level5:{pygame.K_UP:self.level4,pygame.K_DOWN:self.level6},
            self.level6:{pygame.K_UP:self.level5,pygame.K_DOWN:self.button_back},
            self.button_back:{pygame.K_UP:self.level6},
        }
        self.cur_selection = self.level1
        

        self.ui.updateSize(self.screen.width,self.screen.height)
        self.ui.updatePos(0,0)
        
        
        self.sel_rect_pos = LerpThing(pygame.Vector2(self.cur_selection.rect.topleft),4/60,easings.sqrt)
        self.sel_rect_size = LerpThing(pygame.Vector2(self.cur_selection.rect.size),4/60,easings.smoothstep)
        
    def updateSelectionRect(self):
        self.sel_rect_pos.setValue(pygame.Vector2(self.cur_selection.rect.topleft))
        self.sel_rect_size.setValue(pygame.Vector2(self.cur_selection.rect.size))

    def Start(self):
        self.ui.updateSize(self.screen.width,self.screen.height)
        self.ui.updatePos(0,0)
        self.sel_rect_pos.setImmediate(pygame.Vector2(self.cur_selection.rect.topleft))
        self.sel_rect_size.setImmediate(pygame.Vector2(self.cur_selection.rect.size))
        return super().Start()

    def doButton(self):
        def transitionToScene(scene:Scene):
            if False: yield
            self.state_m.stopScene(self)
            self.state_m.startScene(scene)
        
        match self.cur_selection.texts:
            case 'Level 1':
                self.state_m.level.setup(self.state_m.main_levels[0])
                self.state_m.async_ctx.add(transitionToScene(self.state_m.level))
            case 'Level 2':
                self.state_m.level.setup(self.state_m.main_levels[1])
                self.state_m.async_ctx.add(transitionToScene(self.state_m.level))
            case 'Level 3':
                self.state_m.level.setup(self.state_m.main_levels[2])
                self.state_m.async_ctx.add(transitionToScene(self.state_m.level))
            case 'Level 4':
                self.state_m.level.setup(self.state_m.main_levels[3])
                self.state_m.async_ctx.add(transitionToScene(self.state_m.level))
            case 'Level 5':
                self.state_m.level.setup(self.state_m.main_levels[4])
                self.state_m.async_ctx.add(transitionToScene(self.state_m.level))
            case 'Level 6':
                self.state_m.level.setup(self.state_m.main_levels[5])
                self.state_m.async_ctx.add(transitionToScene(self.state_m.level))
            case 'Back':
                self.state_m.async_ctx.add(transitionToScene(self.state_m.main_menu))


    def handleEvent(self, event: Event):
        if event.type == pygame.WINDOWRESIZED:
            self.ui.updateSize(event.x,event.y)
            self.ui.updatePos(0,0)
            self.sel_rect_pos.setImmediate(pygame.Vector2(self.cur_selection.rect.topleft))
            self.sel_rect_size.setImmediate(pygame.Vector2(self.cur_selection.rect.size))


        elif event.type == pygame.KEYDOWN:
            hooks = self.selections[self.cur_selection]
            transition_to = hooks.get(event.key)
            if transition_to is not None:
                self.cur_selection = transition_to
                self.updateSelectionRect()
            elif event.key == pygame.K_z:
                self.doButton()
                return True

        if self.ui.handleEvent(event):
            return True
        return super().handleEvent(event)
    
    def Update(self, keys: ScancodeWrapper, keys_down: ScancodeWrapper, keys_up: ScancodeWrapper):
        for button in self.selections:
            if button.clicked():
                if self.cur_selection == button:
                    self.doButton()
                else:
                    self.cur_selection = button
                    self.updateSelectionRect()

        return super().Update(keys, keys_down, keys_up)
    
    def Draw(self):
        pygame.draw.rect(self.screen,'red',(self.sel_rect_pos.getValue(),self.sel_rect_size.getValue()),2,5)
        self.ui.draw(self.screen)

        
        