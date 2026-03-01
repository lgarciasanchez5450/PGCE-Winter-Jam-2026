from typing import Any
import pygame
from Engine import *
from Scripts import SerializeHelper
from Editor.Hierarchy import Hierarchy
from Editor.Inspector import Inspector
        
def main():
    window = pygame.Window(resizable=True)
    editor_engine = Engine(window.get_surface())
    editor_engine.addSystem(Hierarchy,'',pygame.Rect(0,0,200,400),EngineState.empty().serialize())
    editor_engine.addSystem(Inspector,'',pygame.Rect(window.size[0]-200,0,200,400))
    
    hierarchy = editor_engine.getSystem(Hierarchy)
    inspector = editor_engine.getSystem(Inspector)
    
    editor_engine.Initialize()
    clock = pygame.Clock()
    editor_engine.running = True
    editor_engine.broadcastEvent(EngineEvent.STARTED)
    while editor_engine.running:
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_engine.running = False
            elif event.type == pygame.WINDOWRESIZED:
                
                print(event)
            else:
                events.append(event)
        editor_engine.Update(events)
        editor_engine.Draw()
        window.flip()
        editor_engine.dt = clock.tick(60) / 1_000
        

    
    
        
           
if __name__ == '__main__':
    pygame.init()
    main()