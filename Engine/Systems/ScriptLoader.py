import importlib
import types
from System import BaseSystem


class ScriptLoader(BaseSystem):
    def __init__(self):
        self.scripts:dict[str,types.ModuleType] = {}

    def loadScript(self,path:str):    
        script = importlib.import_module(path)
        self.scripts[path] = script
        return script

    def update(self): pass

    def draw(self): pass