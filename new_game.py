import pygame
from Scripts.MainMenu import MainMenu
from Scripts import SerializeHelper
from Engine import *
if __name__ == '__main__':
    pygame.init()
    window = pygame.Window(resizable=True)
    engine = Engine(window.get_surface())
    engine.addSystem(MainMenu,'')
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
