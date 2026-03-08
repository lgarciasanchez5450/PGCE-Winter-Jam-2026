import pygame
from Scripts.MainMenu import MainMenu
from Scripts.LevelMenu import LevelMenu
from Scripts.Camera import Camera
from Scripts.MapDrawer import MapDrawer
from Scripts.Level import LevelSystem
from Scripts.GameData import GameData
from gameSim import defaultGameStateParameters, generateInterestingGameStates
from Scripts import SerializeHelper
from Engine import *
if __name__ == '__main__':
    pygame.init()
    window = pygame.Window(resizable=True)
    engine = Engine(window.get_surface())
    engine.addSystem(GameData,'data',True)
    
    main_menu_scene = EngineState.empty()
    engine.addSystemToState(main_menu_scene,MainMenu,'',False)
    engine.addScene('main menu',main_menu_scene)
    
    
    level_menu_scene = EngineState.empty()
    engine.addSystemToState(level_menu_scene,LevelMenu,'',False)
    engine.addScene('level menu',level_menu_scene)
    
    
    level_scene = EngineState.empty()
    engine.addSystemToState(level_scene,Camera,'',False,pygame.Vector2())
    engine.addSystemToState(level_scene,MapDrawer,'',False,[],[])
    engine.addSystemToState(level_scene,LevelSystem,'',False,next(generateInterestingGameStates(1,defaultGameStateParameters))[0])
    engine.addScene('level',level_scene)

    
    engine.loadState(engine.getScene('main menu'))
    engine.Initialize()
    clock = pygame.Clock()
    engine.running = True
    engine.broadcastEvent(EngineEvent.STARTED)
    while engine.running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            engine.running = False
        keysd = pygame.key.get_just_pressed()
        keysu = pygame.key.get_just_released()
        engine.Update(pygame.event.get(),keys,keysd,keysu)
        engine.screen.fill('black')
        engine.Draw()
        window.flip()
        engine.dt = clock.tick(60) / 1_000
