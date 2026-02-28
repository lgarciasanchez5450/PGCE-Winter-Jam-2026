import pygame
import typing
from pygame import Surface

class Drawable(typing.Protocol):
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

class Blit:
    __slots__ = 'source','dest','area','special_flags'
    def __init__(self,source:Surface,dest:pygame.typing.RectLike=(0, 0),area:pygame.typing.RectLike|None=None,special_flags:int=0):
        self.source = source
        self.dest = dest
        self.area = area
        self.special_flags = special_flags
    
    def draw(self,surf:Surface):
        surf.blit(self.source,self.dest,self.area,self.special_flags)
        
class BlitFuture:
    __slots__ = 'source','dest','area','special_flags'
    def __init__(self,source:typing.Callable[[],Surface],dest:pygame.typing.RectLike=(0, 0),area:pygame.typing.RectLike|None=None,special_flags:int=0):
        self.source = source
        self.dest = dest
        self.area = area
        self.special_flags = special_flags
    
    def draw(self,surf:Surface):
        surf.blit(self.source(),self.dest,self.area,self.special_flags)
        
class Future:
    def __init__(self,func:typing.Callable[...,typing.Any],*args,**kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def draw(self,surf:Surface):
        self.func(surf,*self.args,**self.kwargs)
        
class FBlits:
    __slots__ = 'blit_sequence','special_flags'
    def __init__(self,blit_sequence:typing.Iterable[tuple[Surface,pygame.typing.RectLike]],special_flags:int=0):
        self.blit_sequence = blit_sequence
        self.special_flags = special_flags
        
    def draw(self,surf:Surface):
        surf.fblits(self.blit_sequence,self.special_flags)