import typing
import pygame
from pygame import Event, Surface
from pygame.key import ScancodeWrapper
from Engine import *
from Engine import UI as ui
from time import perf_counter
from Scripts import easings

if typing.TYPE_CHECKING:
    from game import Game
    
class Mathable(typing.Protocol):
    def __mul__(self,other:float) -> 'typing.Self': ...
    def __rmul__(self,other:float) -> 'typing.Self': ...
    def __add__(self,other:typing.Any) -> 'typing.Self': ...

    
T = typing.TypeVar('T',bound=Mathable)

    

class Button(ui.Widget):
    def __init__(self,tr:Text.Mapping[str],text:str,color:pygame.typing.ColorLike = 'white',size:tuple[int,int]=(30,30)) -> None:
        super().__init__()
        self.color = color
        self.down = False
        self._clicked = False
        self.width,self.height = size
        self.text = text
        self.tr = tr
        
    def getMinWidth(self) -> int:
        return self.width
    
    def getMinHeight(self) -> int:
        return self.height
        
    def clicked(self):
        if self._clicked:
            self._clicked = False
            return True
        return False

    def handleEvent(self, event: Event):
        if self.down:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    self._clicked = True
                    self.down = False
                else:
                    self.down = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.down = True
        super().handleEvent(event)
        
    def draw(self,surf:pygame.Surface):
        text_surf = self.tr.get(self.text)
        surf.blit(text_surf,text_surf.get_rect(center=self.rect.center))
        
class Image(ui.Widget):
    def __init__(self,surf:pygame.Surface):
        super().__init__()
        self.surf = surf
        self.rect.size = surf.size

    def getMinWidth(self) -> int:
        return self.surf.width
    
    def getMinHeight(self) -> int:
        return self.surf.height
    
    def draw(self, surf: Surface):
        surf.blit(self.surf,self.rect)


class LerpThing(typing.Generic[T]):
    def __init__(self,start:T,dt:float,ease:typing.Callable[[float],float]=lambda x:x):
        self.start = start
        self.ease = ease
        self.dt = dt
        self.t_start = perf_counter()
        self.end = start
    
    def getElapsedTime(self) -> float:    
        return perf_counter() - self.t_start
    
    def setImmediate(self,v:T):
        self.start = self.end = v

    def setValue(self,v:T):
        self.start = self.getValue()
        self.end = v
        self.t_start = perf_counter()
    
    def getValue(self) -> T:
        t = self.getElapsedTime() / self.dt
        if t >= 1:
            return self.end
        t = self.ease(t)
        a = (1-t) * self.start
        b = t * self.end
        return a + b
    
    # def __get__(self,obj,typ) -> T: 
    #     return self.getValue()
    
    # def __set__(self,v:T,obj):
    #     self.setValue(v)


class MainMenu(Scene):
    # sel_rect_pos = LerpThing[pygame.Vector2](pygame.Vector2(),1)
    # sel_rect_size = LerpThing[pygame.Vector2](pygame.Vector2(),1)
    def __init__(self, viewport: Surface, assets: AssetManager,game_state:'Game'):
        super().__init__(viewport, assets)
        self.state_m = game_state
        self.title_surf = assets.get('./Resources/title_card.png',pygame.Surface)
        self.font = assets.get('./EditorAssets/default_font.asset',pygame.Font)
        self.text_renderer = Text.Mapping[str](self.font,True,'white')
        self.createUI()
        
    def createUI(self):
        button_stack = ui.YStack([0])

        self.button1 = Button(self.text_renderer,'button1','red',size=(150,40))
        self.button2 = Button(self.text_renderer,'button2','green',size=(150,40))
        self.button3 = Button(self.text_renderer,'button3','blue',size=(150,40))
        self.selections = {
            self.button1:{pygame.K_DOWN:self.button2},
            self.button2:{pygame.K_UP:self.button1,pygame.K_DOWN:self.button3},
            self.button3:{pygame.K_UP:self.button2},
        }
        self.cur_selection = self.button1
        
        
        self.title_image = Image(self.title_surf)
        
        button_stack.setChildren([
            self.button1,
            ui.Padding(self.button2,[10,0]),
            self.button3
        ])
        xstack = ui.XStack([1])
        xstack.setChildren([ui.Place(self.title_image,0.5,0.5),ui.Place(button_stack,0.5,0.5,0.5)])
        self.ui = ui.Padding(xstack,[20])
        
        self.ui.updateSize(self.screen.width,self.screen.height)
        self.ui.updatePos(0,0)
        self.sel_rect_pos = LerpThing(pygame.Vector2(self.cur_selection.rect.topleft),4/60,easings.sqrt)
        self.sel_rect_size = LerpThing(pygame.Vector2(self.cur_selection.rect.size),4/60,easings.smoothstep)
        
    
    def handleEvent(self, event: Event):
        if event.type == pygame.WINDOWRESIZED:
            self.ui.updateSize(event.x,event.y)
            self.ui.updatePos(0,0)
        elif event.type == pygame.KEYDOWN:
            hooks = self.selections[self.cur_selection]
            transition_to = hooks.get(event.key)
            if transition_to is not None:
                self.cur_selection = transition_to
                self.sel_rect_pos.setValue(pygame.Vector2(self.cur_selection.rect.topleft))
                self.sel_rect_size.setValue(pygame.Vector2(self.cur_selection.rect.size))
        
        if self.ui.handleEvent(event):
            return True
        return super().handleEvent(event)
        
    def Start(self):
        return super().Start()
    
    def Update(self, keys: ScancodeWrapper, keys_down: ScancodeWrapper, keys_up: ScancodeWrapper):
        if self.button1.clicked():
            self.cur_selection = self.button1
        if self.button2.clicked():
            self.cur_selection = self.button2
        if self.button3.clicked():
            self.cur_selection = self.button3
        return super().Update(keys, keys_down, keys_up)
    
    def Draw(self):
        self.screen.fill((14,14,14))
        # pygame.draw.rect(self.screen,'green',self.cur_selection.rect,2,4)
        pygame.draw.rect(self.screen,'red',(self.sel_rect_pos.getValue(),self.sel_rect_size.getValue()),2,5)
        
        # self.screen.blit(self.text_renderer['Press Z to Start'])
        
        self.ui.draw(self.screen)