from Engine import *
# from Engine.Serialize import Writer,Reader

class HierarchyRenderer:
    def __init__(self,hierarchy:'Hierarchy'):
        self.h = hierarchy
        self.title_font = self.h.engine.assets.get('EditorAssets/area_title_font.asset',pygame.Font)
        self.default_font = self.h.engine.assets.get('EditorAssets/default_font.asset',pygame.Font)
        
        self.area_title = Text(self.title_font,True,'white')
        
        self.system_text = Text(self.default_font,True,'white')
    
        self.system_text_to_surf:dict[tuple,pygame.Surface] = {}
        
        
    def draw(self,surf:pygame.Surface):
        self.area_title.setText(self.h.area_title)
        rect = self.h.rect
        pygame.draw.rect(surf,'gray',rect,0,5)
        surf.blit(self.area_title.render(),rect)
        y = rect.top + self.area_title.render().height + 5
        
        for system in self.h.engine_state.systems:
            name = system[1]
            cached = self.system_text_to_surf.get(system)
            if cached is None:
                self.system_text.setText(name)
                cached = self.system_text.render()
                self.system_text_to_surf[system] = cached
                
            surf.blit(cached,(rect.left+10,y))
            y += cached.height + 4
            
        
class Hierarchy(BaseSystem[pygame.Rect,bytes]):
    def setState(self,rect:pygame.Rect,systems:bytes):
        self.rect = rect
        self.engine_state = EngineState.deserialize(systems)

    def getState(self):
        return (self.rect,self.engine_state.serialize())
        
    def init(self):
        self.renderer = HierarchyRenderer(self)
        self.area_title = 'Hierarchy'
    
    def update(self):
        pass
    
    def draw(self):
        self.engine.draw(self.renderer)
        