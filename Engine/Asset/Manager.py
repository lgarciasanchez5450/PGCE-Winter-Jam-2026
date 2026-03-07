import weakref
from ..Engine import *
from .Loader import *

class RecursiveAssetDefinition(Exception): ...

class AssetManager:
    def __init__(self):
        self.cache:dict[str,weakref.ReferenceType] = {}
        self.asset_type_loaders:dict[type,type[AssetLoader]] = {}
        self._recursive_paths:dict[str,None] = {}
        self.addAssetLoader(pygame.Surface,SurfaceLoader)
        self.addAssetLoader(pygame.Font,FontLoader)
   
    def addAssetLoader[T](self,typ:type[T],loader:type[AssetLoader[T]]):
        if typ in self.asset_type_loaders:
            raise KeyError(f'Duplicate Asset Loader for type \'{typ.__name__}\'')
        self.asset_type_loaders[typ] = loader

    def loadAsset[T](self,path:str,typ:type[T]) -> T:
        '''
        Load the asset in [path] as [type].
        This will return a completely new asset that will not be cached.
        '''
        if path in self._recursive_paths:
            err = f' -> '.join(self._recursive_paths.keys())
            err = f'{err} -> {path}'
            self._recursive_paths.clear()
            raise RecursiveAssetDefinition(err)
        self._recursive_paths[path] = None

        loader:AssetLoader[T] = self.asset_type_loaders[typ](self,path)
        asset = loader.load()
        del self._recursive_paths[path]
        return asset
        
    def get[T](self,path:str,typ:type[T]) -> T:
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
