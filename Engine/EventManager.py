import typing
import pygame


class EventManager:
    def __init__(self,events:list[pygame.Event]):
        self.events = events
        
    def handle(self,handler:typing.Callable[[pygame.Event],bool|None]):
        for event in self.events[:]:
            if handler(event):
                self.events.remove(event)
                
    def __bool__(self):
        return not not(self.events)

    def __repr__(self):
        return f'Events({self.events})'