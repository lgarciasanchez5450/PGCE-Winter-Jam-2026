import typing

from pygame.font import Font
from pygame.surface import Surface

from ..Engine import *
import pygame

if typing.TYPE_CHECKING:
    from .Manager import AssetManager

type TC = typing.Callable[[str],typing.Any]
    
class UnexpectedTypeError(Exception): ...

class AssetLoaderError(Exception): ...


class AssetLoader[T_]:
    
    def __init__(self,asset_manager:'AssetManager'):
        self.asset_manager = asset_manager
    def addDescriptor(self,key:str,value:str): ...
    def build(self) -> T_: ...

class SurfaceLoader(AssetLoader[pygame.Surface]):
    surf:pygame.Surface|None
    stage:int
    def __init__(self, asset_manager: 'AssetManager'):
        super().__init__(asset_manager)    
        self.surf = None
        self.scale_type:typing.Literal['normal','smooth'] = 'normal'
        self.stage = 0
        self._table:dict[str,TC] = {
            'path':self.path,
            'convert':self.convert,
            'scale':self.scale,
            'scale_by':self.scale_by,
            'flip':self.flip,
            'blur':self.blur,
            'scale_type':self.set_scale_type
        }

    
    def path(self,path:str):
        if self.stage != 0: raise AssetLoaderError
        self.surf = pygame.image.load(path)
        self.stage += 1

    def convert(self,typ:str):
        if self.stage != 1: raise AssetLoaderError
        assert self.surf is not None
        
        if typ == 'alpha' or typ == 'a':
            self.surf = self.surf.convert_alpha()
        elif typ == 'opaque' or typ == 'o':
            self.surf = self.surf.convert()

    def set_scale_type(self,typ:str):
        if typ == 'normal':
            self.scale_type = 'normal'
        elif typ == 'smooth':
            self.scale_type = 'smooth'
        else:
            raise AssetLoaderError
        

    def scale(self,s:str):
        if self.stage != 1: raise AssetLoaderError
        assert self.surf is not None
        x,y = [int(x.strip()) for x in s.split(',')]
        if self.scale_type == 'normal':
            self.surf = pygame.transform.scale(self.surf,(x,y))
        else:
            self.surf = pygame.transform.smoothscale(self.surf,(x,y))

    def scale_by(self,s:str):
        if self.stage != 1: raise AssetLoaderError
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
        if self.stage != 1: raise AssetLoaderError
        assert self.surf is not None
        flip_x = False
        flip_y = False
        if 'x' in s:
            flip_x = True
        if 'y' in s:
            flip_y = True
        self.surf = pygame.transform.flip(self.surf,flip_x,flip_y)

    def blur(self,args:str):
        if self.stage != 1: raise AssetLoaderError
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
            
    def addDescriptor(self, key: str, value: str):
        hook = self._table.get(key)
        if hook is None: raise AssetLoaderError(f'')
        try:
            hook(value)
        except AssetLoaderError:
            raise
        except Exception as other_err:
            err_str = str(other_err)
            raise AssetLoaderError(err_str)
        
    def build(self) -> Surface:
        if self.surf is None:
            return pygame.Surface((0,0))
        return self.surf

class FontLoader(AssetLoader[pygame.Font]):
    def __init__(self, asset_manager: 'AssetManager'):
        super().__init__(asset_manager)
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
