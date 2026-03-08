import typing
import pygame

class Text:
    __slots__ = 'font','text','cache','aa','color','bgcolor','wraplength'
    def __init__(self,font:pygame.Font,aa:bool,color:pygame.typing.ColorLike,bgcolor:pygame.typing.ColorLike|None=None,wraplength:int=0):
        self.font = font
        self.aa = aa
        self.color = color
        self.bgcolor = bgcolor
        self.wraplength = wraplength
        self.text = ''
        self.cache = None
        
    def setFont(self,font:pygame.Font):
        if self.cache and self.font == font: return self
        self.font = font
        self.cache = None
        return self
        
    def setText(self,text:str):
        if self.cache and self.text == text: return self
        self.text = text
        self.cache = None
        return self
    
    def setAA(self,aa:bool):
        if self.cache and self.aa == aa: return self
        self.aa = aa
        self.cache = None
        return self
    
    def setColor(self,color:pygame.typing.ColorLike):
        if self.cache and self.color == color: return self
        self.color = color
        self.cache = None
        return self

    def setBGColor(self,bgcolor:pygame.typing.ColorLike):
        if self.cache and self.bgcolor == bgcolor: return self
        self.bgcolor = bgcolor
        self.cache = None
        return self
        
    def setWraplength(self,wraplength:int):
        if self.cache and self.wraplength == wraplength: return self
        self.wraplength = wraplength
        self.cache = None
        return self
        
    def copy(self):
        return Text(self.font,self.aa,self.color,self.bgcolor,self.wraplength).setText(self.text)    
    
    def render(self):
        if self.cache is None:
            self.cache = self.font.render(self.text,self.aa,self.color,self.bgcolor,self.wraplength)
        return self.cache        
    

class Mapping[K]:
    def __init__(self,font:pygame.Font,aa:bool,color:pygame.typing.ColorLike,bgcolor:pygame.typing.ColorLike|None=None,wraplength:int=0,coerce:typing.Callable[[K],str] = str):
        self._text = Text(font,aa,color,bgcolor,wraplength)
        self.cache:dict[K,pygame.Surface] = {}
        self.coerce = coerce
        
    def setFont(self,font:pygame.Font):
        self._text.setFont(font)
        if self._text.cache is None: self.cache.clear()
        return self
        
    def setAA(self,aa:bool):
        self._text.setAA(aa)
        if self._text.cache is None: self.cache.clear()
        return self
    
    def setColor(self,color:pygame.typing.ColorLike):
        self._text.setColor(color)
        if self._text.cache is None: self.cache.clear()
        return self

    def setBGColor(self,bgcolor:pygame.typing.ColorLike):
        self._text.setBGColor(bgcolor)
        if self._text.cache is None: self.cache.clear()
        return self

    def setWraplength(self,wraplength:int):        
        self._text.setWraplength(wraplength)
        if self._text.cache is None: self.cache.clear()
        return self

    def get(self,k:K) -> pygame.Surface:
        if (surf:= self.cache.get(k)) is not None:
            return surf
        self._text.setText(self.coerce(k))
        surf = self._text.render()
        self.cache[k] = surf
        return surf
    
        
    
    def __getitem__(self,k:K) -> pygame.Surface:
        return self.get(k)
        
    
    def inCache(self,k:K) -> bool:
        return k in self.cache
    
        
        
        
        
    
        
    