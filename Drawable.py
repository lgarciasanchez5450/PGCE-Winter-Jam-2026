from pygame import Surface
from typing import Protocol
import pygame

class Drawable(Protocol):
    def draw(self,surf:Surface): ...
    
class Rect:
    __slots__ = 'color','rect','width','border_radius','border_top_left_radius','border_top_right_radius','border_bottom_left_radius','border_bottom_right_radius',
    def __init__(self,
        color: pygame.typing.ColorLike,
        rect: pygame.typing.RectLike,
        width: int = 0,
        border_radius: int = -1,
        border_top_left_radius: int = -1,
        border_top_right_radius: int = -1,
        border_bottom_left_radius: int = -1,
        border_bottom_right_radius: int = -1
) -> None:
        self.color = color
        self.rect = rect
        self.width = width
        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius
        
    def draw(self,surf:Surface):
        pygame.draw.rect(
            surf,
            self.color,
            self.rect,
            self.width,
            self.border_radius,
            self.border_top_left_radius,
            self.border_top_right_radius,
            self.border_bottom_left_radius,
            self.border_bottom_right_radius,
        )