from pygame import Event, Surface
from pygame.key import ScancodeWrapper

from Engine import *
from Engine.Asset.Manager import AssetManager
from Engine.Text import Mapping
from Engine import UI as ui
from Scripts.MainMenuScene import Button,LerpThing
from Scripts import easings
import typing

if typing.TYPE_CHECKING:
    from game import Game
class SwitchingButton(Button):
    def __init__(self, tr: Mapping[str], text: list[str],i:int, size: tuple[int, int] = (10,10)) -> None:
        
        super().__init__(tr, text[i], size)
        self.texts = text
        self.i = i
        
        
    def draw(self, surf: Surface):
        text_surf = self.tr.get(self.texts[self.i])
        surf.blit(text_surf,text_surf.get_rect(center=self.rect.center))

class SettingsScene(Scene):
    def __init__(self, viewport: Surface, assets: AssetManager,state_m:'Game'):
        super().__init__(viewport, assets)
        self.state_m = state_m
        self.font = assets.get('./Assets/default_font.asset',pygame.Font)
        self.tr = Text.Mapping[str](self.font,True,'white')
        self.createUI()
        
    def createUI(self):
        ystack = ui.YStack()
        self.sfx_button = SwitchingButton(self.tr,['Mute SFX','Unmute SFX'],int(self.state_m.sfx_muted),(200,50))
        self.music_button = SwitchingButton(self.tr,['Mute Music','Unmute Music'],int(self.state_m.music_muted),(200,50))
        self.endless_dif = SwitchingButton(self.tr,['Endless Difficulty: Easy','Endless Difficulty: Medium','Endless Difficulty: Hard'],['easy','medium','hard'].index(self.state_m.endless_difficulty),size=(200,50))
        self.button_back = Button(self.tr,'Back',(200,50))
        self.selections:dict[Button,dict[int,Button]] = {
            self.sfx_button: {pygame.K_DOWN:self.music_button},
            self.music_button:{pygame.K_UP:self.sfx_button,pygame.K_DOWN:self.endless_dif},
            self.endless_dif:{pygame.K_UP:self.music_button,pygame.K_DOWN:self.button_back},
            self.button_back:{pygame.K_UP:self.endless_dif},
        }
        self.cur_selection = self.sfx_button
        
        ystack.setChildren([
            self.sfx_button,
            self.music_button,
            self.endless_dif,
            self.button_back
        ])
        
        self.ui = ui.Place(ystack,0.5,0.5)

        self.ui.updateSize(self.screen.width,self.screen.height)
        self.ui.updatePos(0,0)
        self.sel_rect_pos = LerpThing(pygame.Vector2(self.cur_selection.rect.topleft),4/60,easings.sqrt)
        self.sel_rect_size = LerpThing(pygame.Vector2(self.cur_selection.rect.size),4/60,easings.smoothstep)
        
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
        
        if isinstance(self.cur_selection,SwitchingButton):
            if self.cur_selection.texts[0] == 'Mute SFX':
                self.cur_selection.i = 1-self.cur_selection.i
                self.state_m.sfx_muted = bool(self.cur_selection.i)
                self.state_m.toggleSFXMute(self.state_m.sfx_muted)
            if self.cur_selection.texts[0] == 'Mute Music':
                self.cur_selection.i = 1-self.cur_selection.i
                self.state_m.music_muted = bool(self.cur_selection.i)
                self.state_m.toggleSongMute(self.state_m.music_muted)
            if self.cur_selection.texts[0].startswith('Endless Difficulty: '):
                self.cur_selection.i += 1
                self.cur_selection.i %= len(self.cur_selection.texts)
                if self.cur_selection == 0:
                    self.state_m.endless_difficulty = 'easy'
                elif self.cur_selection == 1:
                    self.state_m.endless_difficulty = 'medium'
                elif self.cur_selection == 2:
                    self.state_m.endless_difficulty = 'hard'
                
                self.state_m.endless_level.updateDifficulty()
        else:
            if self.cur_selection.texts == 'Back':
                self.state_m.async_ctx.add(transitionToScene(self.state_m.main_menu))
                
        self.ui.updateSize(self.screen.width,self.screen.height)
        self.ui.updatePos(0,0)
        self.updateSelectionRect()

    
    def updateSelectionRect(self):
        self.sel_rect_pos.setValue(pygame.Vector2(self.cur_selection.rect.topleft))
        self.sel_rect_size.setValue(pygame.Vector2(self.cur_selection.rect.size))

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