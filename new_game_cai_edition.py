import pygame
from Scripts.MainMenu import MainMenu
from Scripts.LevelMenu import LevelMenu
from Scripts.Camera import Camera
from Scripts.MapDrawer import MapDrawer
from Scripts.Level import LevelSystem
from Scripts.GameData import GameData
from gameSim import defaultGameStateParameters, generateInterestingGameStates, buildGameStateParametersFunc
from Scripts import SerializeHelper
from Engine import *
if __name__ == '__main__':
    pygame.init()
    assetManager = AssetManager()
    window = pygame.Window(resizable=True)
    engine = Scene(window.get_surface(), assetManager)
    
    gameStateParamtersFunc = buildGameStateParametersFunc(0, 1, 0, 1, 0, 5, 4, 8, 5, 10, 2, 3, 0.25, 0.75)
    gameStateGenerator = generateInterestingGameStates(6,gameStateParamtersFunc)

    engine.addSystem(Camera,'',pygame.Vector2())
    engine.addSystem(MapDrawer,'',[],[])
    engine.addSystem(LevelSystem,'',next(gameStateGenerator)[0])

    engine.Start()
    clock = pygame.Clock()
    running = True
    engine.broadcastEvent(EngineEvent.STARTED)

    pygame.mixer_music.load("./Resources/Audio/Songs/GSong2.wav")
    pygame.mixer_music.play(-1, fade_ms=100)

    while running:
        keys = pygame.key.get_pressed()
        pygame.event.pump()

        if keys[pygame.K_ESCAPE]:
            running = False

        keysd = pygame.key.get_just_pressed()

        keysu = pygame.key.get_just_released()

        if keysd[pygame.K_UP]:
            level = engine.getSystem(LevelSystem)
            nextGameState = next(gameStateGenerator)[0]
            level.setState(nextGameState)
            level.init()

        engine.Update(keys,keysd,keysu)
        engine.screen.fill('black')
        engine.Draw()
        window.flip()
        engine.dt = clock.tick(60) / 1_000
