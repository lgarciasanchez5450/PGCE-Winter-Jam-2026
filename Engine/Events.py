import pygame

class BaseEvent:
    def __init_subclass__(cls,type:int) -> None:
        cls.type = type

class Quit(BaseEvent,type=pygame.QUIT):
    pass
    
class AudioDeviceAdded(BaseEvent,type=pygame.AUDIODEVICEADDED):
    which:int
    iscapture:int

class WindowShown(BaseEvent,type=pygame.WINDOWSHOWN):
    window:pygame.Window

class ActiveEvent(BaseEvent,type=pygame.ACTIVEEVENT):
    gain:int
    state:int
    
class WindowFocusGained(BaseEvent,type=pygame.WINDOWFOCUSGAINED):
    window:pygame.Window
    
class TextEditing(BaseEvent,type=pygame.TEXTEDITING):
    text:str
    start:int
    length:int
    window:pygame.Window
    
class WindowEnter(BaseEvent,type=pygame.WINDOWENTER):
    window:pygame.Window
    
class MouseMotion(BaseEvent,type=pygame.MOUSEMOTION):
    pos:tuple[int,int]
    rel:tuple[int,int]
    buttons:tuple[int,int,int]
    touch:bool
    window:pygame.Window
    
class VideoExpose(BaseEvent,type=pygame.VIDEOEXPOSE):
    pass

class WindowExposed(BaseEvent,type=pygame.WINDOWEXPOSED):
    window:pygame.Window
    
class WindowLeave(BaseEvent,type=pygame.WINDOWLEAVE):
    window:pygame.Window
    
class WindowFocusLost(BaseEvent,type=pygame.WINDOWFOCUSLOST):
    window:pygame.Window
    
class KeyDown(BaseEvent,type=pygame.KEYDOWN):
    unicode:str
    key:int
    mod:int
    scancode:int
    window:pygame.Window

class TextInput(BaseEvent,type=pygame.TEXTINPUT):
    text:str
    window:pygame.Window
    
class KeyUp(BaseEvent,type=pygame.KEYUP):
    unicode:str
    key:int
    mod:int
    scancode:int
    window:pygame.Window
    
class WindowClose(BaseEvent,type=pygame.WINDOWCLOSE):
    window:pygame.Window
    
