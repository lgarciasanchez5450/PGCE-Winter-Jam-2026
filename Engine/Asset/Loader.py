import typing

from pygame.surface import Surface
from ..Engine import *

T = typing.TypeVar('T')
type TC = typing.Callable[[typing.Any,str],typing.Any]
    
class UnexpectedTypeError(Exception): ...

class AssetLoaderError(Exception): ...

class AssetLoader[T_]:
    def addDescriptor(self,key:str,value:str): ...
    def build(self) -> T_: ...


class SurfaceLoader(AssetLoader[pygame.Surface]):
    surf:pygame.Surface|None
    stage:int
    
    
    def __init__(self) -> None:
        self.surf = None
        self.scale_type:typing.Literal['normal','smooth'] = 'normal'
        self.stage = 0
        
    _table:dict[str,TC] = {}
    @staticmethod
    def desc(func:TC):
        SurfaceLoader._table[func.__name__] = func
        return func
    @desc
    def path(self,path:str):
        if self.stage != 0: raise AssetLoaderError
        self.surf = pygame.image.load(path)
        self.stage += 1
    @desc    
    def convert(self,typ:str):
        if self.stage != 1: raise AssetLoaderError
        assert self.surf is not None
        
        if typ == 'alpha' or typ == 'a':
            self.surf = self.surf.convert_alpha()
        elif typ == 'opaque' or typ == 'o':
            self.surf = self.surf.convert()
    @desc        
    def scale(self,s:str):
        if self.stage != 1: raise AssetLoaderError
        assert self.surf is not None
        x,y = [int(x.strip()) for x in s.split(',')]
        if self.scale_type == 'normal':
            self.surf = pygame.transform.scale(self.surf,(x,y))
        else:
            self.surf = pygame.transform.smoothscale(self.surf,(x,y))
    @desc
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
    @desc   
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
    @desc
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
        if hook is None: raise AssetLoaderError
        try:
            hook(self,value)
        except AssetLoaderError:
            raise
        except Exception as other_err:
            err_str = str(other_err)
            raise AssetLoaderError(err_str)
        
    def build(self) -> Surface:
        if self.surf is None:
            return pygame.Surface((0,0))
        return self.surf
        



