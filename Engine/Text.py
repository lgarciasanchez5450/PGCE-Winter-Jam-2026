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