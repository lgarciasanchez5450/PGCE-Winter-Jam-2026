import sys
import typing
import pygame
from Engine import *
from Scripts.Map import Map
from Scripts.Camera import Camera
from Scripts.LevelMenuScene import LevelMenu
from Scripts.GameData import GameData
# from Scripts.MainMenu import MainMenu
from Scripts.MainMenuScene import MainMenu
from Scripts.LevelScene import LevelScene
from Scripts.SettingsScene import SettingsScene
from Scripts.Animation import AnimationLoader,Animation
from Scripts import SerializeHelper
from Scripts import Coros
from gameSim import GameState,generateInterestingGameStates,defaultGameStateParameters,GameStateGenerationParameters


class Game:

    def __init__(self):
        self.running_scenes:list[Scene] = []
        self.running = False
        
        self.window = pygame.Window(resizable=True)
        self.w_fullscreen = False
        self.screen = self.window.get_surface()
        self.asset_manager = AssetManager()
        self.asset_manager.addAssetLoader(Animation,AnimationLoader)
        self.async_ctx = Async.Context()
        self.clock = pygame.Clock()
        self.data = GameData()
        self.sfx_muted = False
        self.music_muted = False 
        self.endless_difficulty:typing.Literal['easy','medium','hard'] = 'easy'
        self.level = LevelScene(self.screen,self.asset_manager,self)
        self.main_menu = MainMenu(self.screen,self.asset_manager,self)
        self.settings = SettingsScene(self.screen,self.asset_manager,self)
        self.level_menu = LevelMenu(self.screen,self.asset_manager,self)
        
        
        
        def f():
            params = defaultGameStateParameters()
            params.node_amounts_remaining[GameStateGenerationParameters.TP_NODE] = 1
            params.node_amounts_remaining[GameStateGenerationParameters.FR_NODE] = 1
            params.node_amounts_remaining[GameStateGenerationParameters.FR_NODE] = 1
            params.node_amounts_remaining[GameStateGenerationParameters.N_NODE] = 8
            params.edge_amounts_remaining[GameStateGenerationParameters.N_EDGE] += 1
            return params
        
        gen = generateInterestingGameStates(5,f)
        self.main_levels:list[GameState] = [
            next(gen)[0], # 1
            next(gen)[0], # 2
            next(gen)[0], # 3
            next(gen)[0], # 4
            next(gen)[0], # 5
            next(gen)[0], # 6
        ]
        self.startScene(self.main_menu)

    def handleEvent(self,event:pygame.Event):
        if event.type == pygame.QUIT:
            self.running = False
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                if self.w_fullscreen:
                    self.window.set_windowed()
                else:
                    self.window.set_fullscreen(True)
                self.w_fullscreen = not self.w_fullscreen
                return True
                
                
        
    def startScene(self,scene:Scene):
        if not scene.Start(): raise RuntimeError
        self.running_scenes.append(scene)
        
    def stopScene(self,scene:Scene):
        if not scene.Stop(): raise RuntimeError
        self.running_scenes.remove(scene)
        
    def run(self):
        if self.running: raise RuntimeError
        self.running = True

        while self.running:
            keys = pygame.key.get_pressed()
            keysd = pygame.key.get_just_pressed()
            keysu = pygame.key.get_just_released()
            event_manager = EventManager(pygame.event.get())
            # if event_manager:print(event_manager)
            event_manager.handle(self.handleEvent)
            for scene in self.running_scenes:
                event_manager.handle(scene.handleEvent)
                scene.Update(keys,keysd,keysu)

            self.screen.fill('black')
            for scene in self.running_scenes:
                scene.Draw()
            self.async_ctx.tick()
            self.window.flip()
            
            dt = self.clock.tick(60) / 1_000
            
        
            
def main(argv:list[str]):
    if '-t' in sys.argv:
        import debug, os
        tracer = debug.Tracer()
        tracer.outermost_traversal_path = os.path.abspath('..')
        tracer.traceModule_(sys.modules['__main__'],recurse=True)
        tracer.traceModule_(pygame,copy_cls=True,locals_only=True)
        argv_ = argv.copy()
        argv.remove('-t')
        main(argv_)
        tracer.show()
        return
    
    pygame.init()
    game = Game()
    game.run()

           
if __name__ == '__main__':
    main(sys.argv)