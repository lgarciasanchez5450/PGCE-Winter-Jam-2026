from typing import Any
import pygame
from Engine import *
from Scripts import SerializeHelper
from Editor.Hierarchy import Hierarchy
from Editor.Inspector import Inspector
        
def main():
    window = pygame.Window(resizable=True)
    editor_engine = Scene(window.get_surface())
    editor_engine.addSystem(Hierarchy,'',False,pygame.Rect(0,0,200,400),EngineState.empty().serialize())
    editor_engine.addSystem(Inspector,'',False,pygame.Rect(window.size[0]-200,0,200,400))
    
    hierarchy = editor_engine.getSystem(Hierarchy)
    inspector = editor_engine.getSystem(Inspector)
    
    editor_engine.Start()
    clock = pygame.Clock()
    running = True
    editor_engine.broadcastEvent(EngineEvent.STARTED)
    while running:
        
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.WINDOWRESIZED:
                
                print(event)
            else:
                events.append(event)
        keys = pygame.key.get_pressed()
        keysd = pygame.key.get_just_pressed()
        keysu = pygame.key.get_just_released()
        editor_engine.Update(events,keys,keysd,keysu)
        editor_engine.Draw()
        window.flip()
        editor_engine.dt = clock.tick(60) / 1_000
        

    
    
        
           
if __name__ == '__main__':
    pygame.init()
    main()