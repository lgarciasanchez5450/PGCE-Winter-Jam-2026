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
    
    engine.addSystem(Camera,'',False,pygame.Vector2())
    engine.addSystem(MapDrawer,'',False,[],[])
    engine.addSystem(LevelSystem,'',False,next(generateInterestingGameStates(1,defaultGameStateParameters))[0])

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

        if keysd[pygame.K_UP]:
            level = engine.getSystem(LevelSystem)
            level.setState(next(generateInterestingGameStates(1,defaultGameStateParameters))[0])
            level.init()

        engine.Update(pygame.event.get(),keys,keysd,keysu)
        engine.screen.fill('black')
        engine.Draw()
        window.flip()
        engine.dt = clock.tick(60) / 1_000
