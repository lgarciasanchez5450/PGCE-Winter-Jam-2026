from pygame import Surface

from Engine import *
import typing
if typing.TYPE_CHECKING:
    from game import Game

class LevelMenu(Scene):
    def __init__(self, viewport: Surface, assets: AssetManager,game_state:'Game'):
        super().__init__(viewport, assets)
        self.state_m = game_state
        self.grid_w = 7
        
        
    
    
    def Draw(self):
        surf = self.screen
        rect = surf.get_rect()
        
        rect.inflate_ip(-100,-100)        
        pygame.draw.rect(surf,(100,200,100),rect,0,10)
        
        
        grid_w = self.grid_w
        padding = 10
        level_width = 50
        level_height = 50
        total_width = rect.width
        spacing = (total_width - 2*padding - grid_w*level_width)/(grid_w-1)
        #total_width = 2*padding + grid_w*level_width+(grid_w-1)*spacing
        
        
        for i,level in enumerate(self.state_m.data.levels):
            x = i % grid_w
            y = i // grid_w

            offset_x = int(x * level_width + x*spacing) + padding
            offset_y = int(y * level_height + y*spacing) + padding
            r = pygame.Rect(rect.left+offset_x,rect.top+ offset_y,level_width,level_height)
            
            # self.drawLevel(surf,i,level,r,i==self.menu.current_level_i)
            
    # def drawLevel(self,surf:pygame.Surface,num:int,level:Level,r:pygame.Rect,selected:bool):
    #     if level.completed:
    #         pygame.draw.rect(surf,'dark green',r,0,4)
    #     else:
    #         pygame.draw.rect(surf,'dark gray',r,0,4)
    #     if selected:
    #         pygame.draw.rect(surf,'gold',r,3,4)
    #     else:
    #         pygame.draw.rect(surf,'gray',r,3,4)
            
        
    #     s = self.text[num+1]
    #     surf.blit(s,s.get_rect(center=r.center))
        