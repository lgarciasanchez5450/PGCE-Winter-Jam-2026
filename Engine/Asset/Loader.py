import typing
import pygame

from pygame.font import Font
from pygame.surface import Surface

from ..Engine import *
from ..Parser import LiteralParser

if typing.TYPE_CHECKING:
    from .Manager import AssetManager

class AssetSyntaxError(Exception): ...
    
class UnexpectedTypeError(Exception): ...

class AssetLoaderError(Exception): ...


class AssetLoader[T_]:
    __slots__ = 'asset_manager','path'
    def __init__(self,asset_manager:'AssetManager',path:str):
        self.asset_manager = asset_manager
        self.path = path
    
    def load(self) -> T_:
        with open(self.path) as file:
            contents = file.read()
        
        for line in contents.splitlines():
            if not line: continue
            if line.startswith('//'): continue
            key,_,value = line.partition(':')
            if not _:
                raise AssetSyntaxError(f'Invalid Line in {self.path}: {repr(line)}')
            self.addDescriptor(key.strip(),value.strip())
        return self.build()

        
    def addDescriptor(self,key:str,value:str): ...
    def build(self) -> T_: ...

class SurfaceLoader(AssetLoader[pygame.Surface]):
    surf:pygame.Surface|None
    stage:int
    def __init__(self, asset_manager: 'AssetManager',path:str):
        super().__init__(asset_manager,path)
        self.surf = None
        self.scale_type:typing.Literal['normal','smooth'] = 'normal'
        self.draw_color:pygame.typing.ColorLike = 'white'
        self.stage = 0
        self._table:dict[str,typing.Callable[[str],typing.Any]] = {
            'path':self.path_,
            'empty':self.empty,
            'convert':self.convert,
            'colorkey':self.colorkey,
            'scale':self.scale,
            'scale_by':self.scale_by,
            'flip':self.flip,
            'blur':self.blur,
            'scale_type':self.set_scale_type,
            # The following methods are pygame.draw aliases / helpers for them
            'draw_color':self.set_draw_color,
            'fill':self.fill,
            'line':self.line,
            'rect':self.rect,
        }

    def ensureStage(self,stage:int,ctx:str):
        if self.stage != stage: raise AssetLoaderError(f'{ctx} expects stage: {stage} got {self.stage}')

    def load(self) -> Surface:
        if self.path.endswith('.asset'):
            return super().load()
        else:
            return pygame.image.load(self.path)
    
    def path_(self,path:str):
        self.ensureStage(0,'parh')
        if path.endswith('.asset'):
            self.surf = self.asset_manager.loadAsset(path,Surface)
        else:
            self.surf = pygame.image.load(path)
        self.stage += 1
        
    def empty(self,s:str):
        self.ensureStage(0,'empty')
        w,h = [int(x.strip()) for x in s.split(',')]
        self.surf = pygame.Surface((w,h))
        self.stage += 1

    def convert(self,typ:str):
        self.ensureStage(1,'convert')
        assert self.surf is not None
        
        if typ == 'alpha' or typ == 'a':
            self.surf = self.surf.convert_alpha()
        elif typ == 'opaque' or typ == 'o':
            self.surf = self.surf.convert()

    def colorkey(self,s:str):
        self.ensureStage(1,'colorkey')
        assert self.surf is not None
        try:
            parser = LiteralParser(s)
            color = parser.parse()
            flags = parser.parse() if not parser.done() else 0
        except:
            color = s
            flags = 0
        if color in pygame.color.THECOLORS:
            colorkey = pygame.color.THECOLORS[color]
        else:
            channels = [int(x.strip()) for x in s.split(',')]
            if len(channels) == 1:
                colorkey = channels[0]
            elif len(channels) == 3:
                colorkey = channels
            else:
                raise AssetLoaderError
        self.surf.set_colorkey(colorkey,flags)

    def set_scale_type(self,typ:str):
        if typ == 'normal':
            self.scale_type = 'normal'
        elif typ == 'smooth':
            self.scale_type = 'smooth'
        else:
            raise AssetLoaderError
   
    def scale(self,s:str):
        self.ensureStage(1,'scale')
        assert self.surf is not None
        x,y = [int(x.strip()) for x in s.split(',')]
        if self.scale_type == 'normal':
            self.surf = pygame.transform.scale(self.surf,(x,y))
        else:
            self.surf = pygame.transform.smoothscale(self.surf,(x,y))

    def scale_by(self,s:str):
        self.ensureStage(1,'scale_by')
        assert self.surf is not None
        scale = [int(x.strip()) for x in s.split(',')]
        if len(scale) == 1:
            scale = scale[0]
        elif len(scale) > 2:
            raise AssetLoaderError
        if self.scale_type == 'normal':
            self.surf = pygame.transform.scale_by(self.surf,scale)
        else:
            self.surf = pygame.transform.smoothscale_by(self.surf,scale)

    def flip(self,s:str):
        self.ensureStage(1,'flip')
        assert self.surf is not None
        flip_x = False
        flip_y = False
        if 'x' in s:
            flip_x = True
        if 'y' in s:
            flip_y = True
        self.surf = pygame.transform.flip(self.surf,flip_x,flip_y)

    def blur(self,args:str):
        self.ensureStage(1,'blur')
        assert self.surf is not None
        arglist = [x.strip() for x in args.split(',')]
        if len(arglist) != 2:
            raise AssetLoaderError
        typ,radius = arglist
        
        if typ == 'box':
            self.surf = pygame.transform.box_blur(self.surf,int(radius))
        elif typ == 'gaussian':
            self.surf = pygame.transform.gaussian_blur(self.surf,int(radius))
        else:
            raise AssetLoaderError
            
    def set_draw_color(self,s:str):
        if s in pygame.color.THECOLORS:
            self.draw_color = pygame.color.THECOLORS[s]
            return 
        channels = [int(x.strip()) for x in s.split(',')]
        if len(channels) == 1:
            self.draw_color = channels[0]
        elif len(channels) == 3:
            self.draw_color = channels
        else:
            raise AssetSyntaxError
        
    def line(self,s:str):
        self.ensureStage(1,'line')
        assert self.surf is not None
        parser = LiteralParser(s)
        
        start_pos = parser.parse()
        end_pos = parser.parse()
        if parser.done():
            width = 1
        else:
            width = parser.parse()
        pygame.draw.line(self.surf,self.draw_color,start_pos,end_pos,width)

    def rect(self,s:str):
        self.ensureStage(1,'rect')
        assert self.surf is not None
        parser = LiteralParser(s)
        rect = parser.parse()
        width = parser.parse() if not parser.done() else 0
        border_radius = parser.parse() if not parser.done() else -1
        pygame.draw.rect(self.surf,self.draw_color,rect,width,border_radius)

    def fill(self,s:str):
        self.ensureStage(1,'fill')
        assert self.surf is not None
        if s: raise AssetLoaderError
        self.surf.fill(self.draw_color)
            
    def addDescriptor(self, key: str, value: str):
        hook = self._table.get(key)
        if hook is None: raise AssetLoaderError
        try:
            hook(value)
        except AssetLoaderError:
            raise
        except Exception as other_err:
            err_str = str(other_err)
            raise
            raise AssetLoaderError(err_str)
        
    def build(self) -> Surface:
        if self.surf is None:
            return pygame.Surface((0,0))
        return self.surf

class FontLoader(AssetLoader[pygame.Font]):
    def __init__(self, asset_manager: 'AssetManager',path:str):
        super().__init__(asset_manager,path)
        self.font_orders:list[tuple[str,bool,int]] = []
        self.is_sysfont = False
        self.size = -1
    
    def addDescriptor(self, key: str, value: str):
        if key == 'path':
            if self.size < 0: raise AssetLoaderError
            self.font_orders.append((value,False,self.size))
        elif key == 'name':
            if self.size < 0: raise AssetLoaderError
            self.font_orders.append((value,True,self.size))
        elif key == 'size':
            self.size = int(value)

    def build(self) -> Font:
        sysfonts = None #we will only load the system fonts if we need to 
        for name,is_sysfont,size in self.font_orders:
            if is_sysfont:
                if not sysfonts:
                    sysfonts = pygame.font.get_fonts()
                if name in sysfonts:
                    return pygame.font.SysFont(name,size)
            else:
                try:
                    return pygame.font.Font(name,size)
                except FileNotFoundError:
                    pass
        raise AssetLoaderError
