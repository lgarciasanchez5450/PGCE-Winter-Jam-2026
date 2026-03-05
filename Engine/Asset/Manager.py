import typing
import weakref
from ..Engine import *
from .Loader import *

T = typing.TypeVar('T')
class AssetSyntaxError(Exception): ...
class AssetManager:
    def __init__(self):
        self.cache:dict[str,weakref.ReferenceType] = {}
        self.asset_type_loaders:dict[type,type[AssetLoader]] = {}
        self.addAssetLoader(pygame.Surface,SurfaceLoader)
        self.addAssetLoader(pygame.Font,FontLoader)
   
    def addAssetLoader(self,typ:type[T],loader:type[AssetLoader[T]]):
        if typ in self.asset_type_loaders:
            raise KeyError
        self.asset_type_loaders[typ] = loader

    def loadAsset(self,path:str,typ:type[T]) -> T:
        '''
        Load the asset in [path] as [type].
        This will return a completely new asset that will not be cached.
        '''
        with open(path) as file:
            contents = file.read()
        loader:AssetLoader[T] = self.asset_type_loaders[typ](self)
        
        for line in contents.splitlines():
            if not line: continue
            key,_,value = line.partition(':')
            if not _:
                raise AssetSyntaxError(f'Invalid Line in {path}: {repr(line)}')
            loader.addDescriptor(key.strip(),value.strip())
        return loader.build()

    def get(self,path:str,typ:type[T]) -> T:
        '''
        Get an asset in [path] as [type].
        Asset will be cached and reused for future AssetManager.get calls
        '''
        if (cached:=self.cache.get(path)) is not None:
            ref = cached()
            if ref is not None:
                return ref
        out = self.loadAsset(path,typ)
        if not isinstance(out,typ):
            raise UnexpectedTypeError(f'Expected Type: {typ} got {type(out)}')
        self.cache[path] = weakref.ReferenceType(out)
        return out
