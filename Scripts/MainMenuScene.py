from pygame import Event, Surface
from pygame.key import ScancodeWrapper
from Engine import *
from Engine import UI as ui

import typing
if typing.TYPE_CHECKING:
    from game import Game

class Button(ui.Widget):
    def __init__(self,color:pygame.typing.ColorLike = 'white') -> None:
        super().__init__()
        self.color = color
        
    def draw(self,surf:pygame.Surface):
        pygame.draw.rect(surf,self.color,self.rect,4,8)
        

class MainMenu(Scene):
    def __init__(self, viewport: Surface, assets: AssetManager,game_state:'Game'):
        super().__init__(viewport, assets)
        self.state_m = game_state
        self.title_surf = assets.get('./Resources/title_card.png',pygame.Surface)
        self.font = assets.get('./EditorAssets/default_font.asset',pygame.Font)
        self.text_renderer = Text.Mapping[str](self.font,True,'black','white')
        
        self.ui = ui.YStack([1])
        self.button1 = Button('red')
        self.button2 = Button('green')
        self.button3 = Button('blue')
        self.ui.setChildren([self.button1,ui.Padding(self.button2,[10]),self.button3])
        self.ui = ui.Padding(self.ui,[0,20,0])
        
        self.ui.updateSize(self.screen.width,self.screen.height)
        self.ui.updatePos(0,0)
    
    def handleEvent(self, event: Event):
        if event.type == pygame.WINDOWRESIZED:
            self.ui.updateSize(event.x,event.y)
            self.ui.updatePos(0,0)
            print(self.ui.rect)
            
        return super().handleEvent(event)
        
    def Start(self):
        return super().Start()
    
    def Update(self, keys: ScancodeWrapper, keys_down: ScancodeWrapper, keys_up: ScancodeWrapper):
        return super().Update(keys, keys_down, keys_up)
    
    def Draw(self):
        self.screen.fill('purple')
        self.screen.blit(self.title_surf,self.title_surf.get_rect(center=self.screen.get_rect().center))
        self.screen.blit(self.text_renderer['Press Z to Start'])
        
        self.button1.draw(self.screen)
        self.button2.draw(self.screen)
        self.button3.draw(self.screen)
        
        