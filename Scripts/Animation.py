from pygame import Surface
from Engine import *
from Engine.Asset import Loader

class Animation:
    frames:list[Surface]
    fps:float
    
    
class AnimationLoader(Loader.AssetLoader[Animation]):
    def __init__(self, asset_manager: 'Loader.AssetManager', path: str):
        super().__init__(asset_manager, path)
        self.frames:list[Surface] = []
        self.fps = None
        
    def addDescriptor(self, key: str, value: str):
        if key == 'frame':
            self.frames.append(self.asset_manager.loadAsset(value,pygame.Surface))
        elif key == 'fps':
            self.fps = int(value)

    def build(self):
        if self.fps is None: 
            raise Loader.AssetLoaderError
        out = Animation()
        out.frames = self.frames
        out.fps = self.fps
        return out