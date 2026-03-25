import asyncio
import sys
import typing
import pygame
from Engine import *
from Scripts.LevelMenuScene import LevelMenu
from Scripts.GameData import GameData
# from Scripts.MainMenu import MainMenu
from Scripts.MainMenuScene import MainMenu
from Scripts.LevelScene import LevelScene
from Scripts.EndlessLevelScene import LevelSceneEndless
from Scripts.SettingsScene import SettingsScene
from Scripts.Animation import AnimationLoader,Animation
from Engine import Serialize
from Scripts import SerializeHelper
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
        self.endless_difficulty:typing.Literal['easy','medium','hard'] = 'medium'

        self.sounds = {
            "move" : pygame.Sound("./Resources/Audio/SFX/Move/Gmove1.ogg"),
            "freeze" : pygame.Sound("./Resources/Audio/SFX/Freeze/Gfreeze3.ogg"),
            "explode" : pygame.Sound("./Resources/Audio/SFX/Explode/Gexplosion1.ogg"),
            "teleport" : pygame.Sound("./Resources/Audio/SFX/Teleport/Gteleport3.ogg"),
            "levelReset" : pygame.Sound("./Resources/Audio/SFX/LevelReset/GlevelReset.ogg"),
            "changeEdge" : pygame.Sound("./Resources/Audio/SFX/ChangeEdge/GchangeEdge2.ogg"),
            "levelComplete" : pygame.Sound("./Resources/Audio/SFX/LevelComplete/GlevelComplete1.ogg"),
        } 

        pygame.mixer_music.load("./Resources/Audio/Songs/GSong2.ogg")
        pygame.mixer_music.play(-1)

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
        self.level = LevelScene(self.screen,self.asset_manager,self)
        self.main_menu = MainMenu(self.screen,self.asset_manager,self)
        self.endless_level = LevelSceneEndless(self.screen,self.asset_manager,self)
        self.loadPersistentData()
        self.settings = SettingsScene(self.screen,self.asset_manager,self)
        self.level_menu = LevelMenu(self.screen,self.asset_manager,self)
        self.startScene(self.main_menu)
    
    def toggleSFXMute(self, muted:bool):
        if muted:
            volume = 0
        else:
            volume = 0.5

        for sfx in self.sounds.values():
            sfx.set_volume(volume)
        
    def toggleSongMute(self, muted:bool):
        if muted:
            pygame.mixer_music.set_volume(0)
        else:
            pygame.mixer_music.set_volume(1)

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
                
    def loadPersistentData(self):
        try:
            if sys.platform == 'emscripten':
                raise Exception
            with open('settings','rb') as file:
                reader = Serialize.Reader(file.read())
            self.sfx_muted = reader.readBool()
            self.music_muted = reader.readBool()
            self.endless_difficulty = reader.readStr() # type: ignore
        except:
            return
        finally:
            self.toggleSFXMute(self.sfx_muted)
            self.toggleSongMute(self.music_muted)
            self.endless_level.updateDifficulty(self.endless_difficulty)
        
    def savePersistentData(self):
        writer = Serialize.Writer()
        writer.writeBool(self.sfx_muted)
        writer.writeBool(self.music_muted)
        writer.writeStr(self.endless_difficulty)
        try:
            with open('settings','wb') as file:
                file.write(writer.buf)
        except:
            pass
    def startScene(self,scene:Scene):
        if not scene.Start(): raise RuntimeError
        self.running_scenes.append(scene)
        
    def stopScene(self,scene:Scene):
        if not scene.Stop(): raise RuntimeError
        self.running_scenes.remove(scene)
        
    async def run(self):
        if self.running: raise RuntimeError
        self.running = True
        print('RUNNING!!!!')
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
            await asyncio.sleep(0)  
            
        self.savePersistentData()
            
        
            
async def main(argv:list[str]):
    if '-t' in sys.argv:
        import debug, os
        tracer = debug.Tracer()
        tracer.outermost_traversal_path = os.path.abspath('..')
        tracer.traceModule_(sys.modules['__main__'],recurse=True)
        tracer.traceModule_(pygame,copy_cls=True,locals_only=True)
        argv_ = argv.copy()
        argv.remove('-t')
        await main(argv_)
        tracer.show()
        return
    
    pygame.init()
    game = Game()
    await game.run()

           
if __name__ == '__main__':
    asyncio.run(main(sys.argv))