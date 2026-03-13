import typing
import numpy as np
from pygame import Surface, Event
from pygame.key import ScancodeWrapper
from Engine import UI as ui
from Engine import *
from gameSim import GameState
from Scripts.MainMenuScene import Button,LerpThing
from Scripts.Particles import Particles,Bucket
from Scripts.MapDrawer import NodeWorld
from Scripts.Animation import Animation
from pygame import gfxdraw
from Scripts import easings
if typing.TYPE_CHECKING:
    from game import Game
    
def blit_at(to:Surface,source:Surface,rect:pygame.Rect,align_x:float=0.5,align_y:float=0.5):
    x = rect.left + int((rect.width-source.width) * align_x)
    y = rect.top + int((rect.height-source.height) * align_y)
    to.blit(source,(x,y))
    
    
def drawArrow(surf:pygame.Surface,color,x:int,y:int,dir:pygame.Vector2):
    pygame.draw.line(surf,color,(x,y),(x,y)+dir,3)
    tip = (x,y)+dir
    tip1 = tip+ (-dir).rotate(30) * 0.2
    tip2 = tip+ (-dir).rotate(-30) * 0.2
    gfxdraw.filled_trigon(surf,int(tip.x),int(tip.y),int(tip1.x),int(tip1.y),int(tip2.x),int(tip2.y),color)
    
    


class LevelScene(Scene):
    def __init__(self, viewport: Surface, assets: AssetManager,game_state:'Game'):
        super().__init__(viewport, assets)
        self.state_m = game_state
        self.font = assets.get('./EditorAssets/default_font.asset',pygame.Font)
        self.tick_font = assets.get('./Assets/tick_font.asset',pygame.Font)
        self.text = Text.Text(self.tick_font,True,'white')
        self.help_text = Text.Text(self.font,True,'white')
        self.help_text.setText('R - Restart  |  LEFT/RIGHT - Change Selection  |  Z - Move Nodes')

        self.tr = Text.Mapping[str](self.font,True,'white')
        self.trb = Text.Mapping[str|int](self.font,True,'black')
        self.createUI()
        self.node_world = NodeWorld()
        self.node_surf = assets.get('./Assets/web_node.asset',pygame.Surface)
        self.node_freeze_surf = assets.get('./Resources/node_blue.png',pygame.Surface)
        self.node_teleport_surf = assets.get('./Resources/node_purple.png',pygame.Surface)
        self.node_explosion_surf = assets.get('./Resources/node_red.png',pygame.Surface)
        self.node_surf_g = self.node_surf.copy()
        self.node_surf_g.set_alpha(100)
        self.particles = Particles()
        self.possible_moves = []

        anim = assets.get('./Assets/particle_gray.asset',Animation)
            
        self.explosion_anim_id = self.particles.addAnimation(anim.frames)
        self.explosion_beha_id = self.particles.addBehaviour(self.updateParticles)
        
    def updateParticles(self,bucket:Bucket,mask:np.ndarray):
        bucket.alive[np.logical_and(bucket.frame+bucket.fps >= bucket.anim_len,mask)] = 0

        
    def setup(self,gameState:GameState):
        self.gameState = gameState
        self.node_world.setNewState(gameState.nodes,gameState.edges)
        self.connections = {(edge.a_node,edge.b_node):edge for edge in gameState.edges}
        self.move_option_i = 0
        self.tick = 0
        self.camera_pos = pygame.Vector2()
        self.taking_input = False
        
    def reset(self):
        self.move_option_i = 0
        self.tick = 0
        self.camera_pos = pygame.Vector2()
        self.taking_input = False
        self.cur_node = self.gameState.start_node
        self.tick = -1
        self.moveToNode(self.gameState.start_node)
        
    def createUI(self):
        pass

    def Start(self):
        self.cur_node = self.gameState.start_node
        self.tick = -1
        self.moveToNode(self.gameState.start_node)
        return super().Start()

    def handleEvent(self, event: Event):
        if event.type == pygame.WINDOWRESIZED:
            pass
        elif event.type == pygame.KEYDOWN:
            
            if self.taking_input:
                if self.possible_moves:
                    if event.key == pygame.K_z: 
                        self.taking_input = False
                        self.moveToNode(self.possible_moves[self.move_option_i])
                    elif event.key == pygame.K_LEFT:
                        self.move_option_i -= 1
                        self.move_option_i %= len(self.possible_moves)
                    elif event.key == pygame.K_RIGHT:
                        self.move_option_i += 1
                        self.move_option_i %= len(self.possible_moves)
                if event.key == pygame.K_r:
                    self.reset()
                    
        return super().handleEvent(event)
    
    def Update(self, keys: ScancodeWrapper, keys_down: ScancodeWrapper, keys_up: ScancodeWrapper):
        self.node_world.update()
        self.particles.update(0.2)
        if self.taking_input:
            self.camera_pos.update(np.floor(self.node_world.getPos(self.cur_node)))
        return super().Update(keys, keys_down, keys_up)
    
    def Draw(self):
        camera_offset= tuple(-self.camera_pos + (self.screen.width//2,self.screen.height//2))
        camera_offset = int(camera_offset[0]),int(camera_offset[1])
        poss = self.node_world.world.getPoss().copy() + camera_offset 
        self.draw(Drawable.BlitFuture(self.text.setText(f'Tick: {self.tick}').render),layer = 2)
        for edge in self.gameState.edges:
            has_collapsed = self.nodeIsExploded(edge.a_node) or self.nodeIsExploded(edge.b_node)
            if has_collapsed: continue
            if not edge.cycle[(self.tick)%len(edge.cycle)]: 
                self.draw(Drawable.Line((50,50,50),poss[edge.a_node],poss[edge.b_node],3),layer=1)
            elif len(edge.cycle) > 1:
                self.draw(Drawable.Line('deeppink3',poss[edge.a_node],poss[edge.b_node],3),layer=1)
            else:
                self.draw(Drawable.Line('white',poss[edge.a_node],poss[edge.b_node],3),layer=1)
        poss2 = poss + (-self.node_surf.width//2,-self.node_surf.height//2)   
        for node_i,node in enumerate(self.gameState.nodes):
            pos = poss2[self.node_world.world.id_to_ind[node_i]]
            if self.nodeIsExploded(node_i): continue
            
            if node.explosion_time != -1: #is explosion
                self.draw(Drawable.Blit(self.node_explosion_surf,pos),layer=1)
                self.draw(Drawable.Blit(self.trb[node.explosion_time],pos+(5,0)),layer=2)
            elif node.freeze_time: #is freeze
                self.draw(Drawable.Blit(self.node_freeze_surf,pos),layer=1)
                self.draw(Drawable.Blit(self.trb[node.freeze_time],pos+(5,0)),layer=2)

            elif node.teleport_to != -1: #is teleport 
                self.draw(Drawable.Blit(self.node_teleport_surf,pos),layer=1)
                self.draw(Drawable.Blit(self.trb[node.teleport_to],pos+(5,0)),layer=2)
                
                self.draw(Drawable.Line('purple',pos,poss[node.teleport_to],3),layer=0)

            else:
                self.draw(Drawable.Blit(self.node_surf,pos),layer=1)
                
            if node_i == self.gameState.end_node:
                self.draw(Drawable.Circle('green',poss[self.node_world.world.id_to_ind[node_i]],16,2),2)
            if node_i == self.cur_node:
                self.draw(Drawable.Circle('blue',poss[self.node_world.world.id_to_ind[node_i]],13,2),2)
           
        # for pos, id in zip(poss + (5,1),self.node_world.world.getIDs(),strict=True): #we no longer draw the ID's
        #     self.draw(Drawable.Blit(self.trb[id],pos),layer=2)
            
        self.draw(Drawable.Blit(self.help_text.render(),self.help_text.render().get_rect(topright = self.screen.get_rect().topright)))
        super().Draw()
        if self.possible_moves and self.taking_input:
            pos = pygame.Vector2(self.node_world.getPos(self.cur_node)+camera_offset)
            dif = self.node_world.getPos(self.possible_moves[self.move_option_i])+camera_offset - pos
            if np.any(dif): # pyright: ignore[reportArgumentType, reportCallIssue].
                drawArrow(self.screen,(10,186,20),int(pos.x),int(pos.y),pygame.Vector2(dif).normalize()*50)
        self.particles.draw(self.screen,camera_offset)
    
    def nodeIsExploded(self,node_i:int):
        node = self.gameState.nodes[node_i]
        return node.explosion_time != -1 and node.explosion_time <= self.tick

    def moveToNode(self,node_to:int):
        node_from = self.cur_node
        dif = self.node_world.getPos(node_to) - self.node_world.getPos(node_from)
        if np.any(dif):
            move_angle = np.atan2(dif[1],dif[0])
        else:
            move_angle = None
        self.cur_node = node_to
        
        self.async_ctx.add(self.simulateStep(move_angle))

    def connection(self,a:int,b:int):
        if a>b: a,b = b,a
        return self.connections.get((a,b))
        
    def calcNewDefaultMoveAndSortOptions(self,keep_angle:float|None=None):
        cur_pos = self.node_world.getPos(self.cur_node)
        positions = self.node_world.world.gets(self.possible_moves)
        rel_positions = positions - cur_pos
        angles = np.atan2(rel_positions[:,1],rel_positions[:,0])
        sort_i = np.argsort(angles)
        self.possible_moves = [self.possible_moves[i] for i in sort_i]
        if keep_angle is not None:
            smallest = 10
            for i in range(len(sort_i)):
                angle_dif = (keep_angle - angles[sort_i[i]] + np.pi) % (2*np.pi) - np.pi
                if abs(angle_dif) < abs(smallest):
                    smallest = angle_dif
                    self.move_option_i = i
        else:
            if self.move_option_i >= len(self.possible_moves):
                self.move_option_i = len(self.possible_moves)-1
            elif self.move_option_i < 0: 
                self.move_option_i = 0   

    def possibleMoves(self,node:int) -> list[int]:
        out:list[int] = []
        for node in range(len(self.gameState.nodes)):
            if node == self.cur_node: continue
            edge = self.connection(self.cur_node,node)
            if edge is None: continue
            if not edge.cycle[self.tick%len(edge.cycle)]: continue
            has_collapsed = self.nodeIsExploded(edge.a_node) or self.nodeIsExploded(edge.b_node)
            if has_collapsed: continue
            out.append(node)
        return out
    
    def simulateStep(self,move_angle):
    
        for _ in range(1+self.gameState.nodes[self.cur_node].freeze_time):
            w = Async.WaitTime.forSeconds(0.2)
            cam_start = self.camera_pos.copy()
            for _ in w:
                t = easings.smoothstep(w.countdown)
                self.camera_pos.update(cam_start*t + (1-t) * self.node_world.getPos(self.cur_node))
                yield
            self.camera_pos.update(self.node_world.getPos(self.cur_node))
            #find all nodes that have exploded this tick and explode them
            self.tick += 1
            for i,node in enumerate(self.gameState.nodes):
                if node.explosion_time != -1 and node.explosion_time == self.tick:
                    self.spawnExplosion(i)
                    
        while self.gameState.nodes[self.cur_node].teleport_to != -1:
            w = Async.WaitTime.forSeconds(0.2)
            self.cur_node = self.gameState.nodes[self.cur_node].teleport_to
            cam_start = self.camera_pos.copy()
            for _ in w:
                t = easings.smoothstep(w.countdown)
                self.camera_pos.update(cam_start*t + (1-t) * self.node_world.getPos(self.cur_node))
                yield
            self.camera_pos.update(self.node_world.getPos(self.cur_node))
        
        if self.cur_node == self.gameState.end_node:
            self.onWin()
            return
            
        self.possible_moves = self.possibleMoves(self.cur_node)
        self.calcNewDefaultMoveAndSortOptions(keep_angle=move_angle)
        self.taking_input = True
        
    def onWin(self):
        self.state_m.stopScene(self)
        
    def spawnExplosion(self,node_i:int):
        pos = self.node_world.getPos(node_i)
        for i in range(12):
            self.particles.addParticle(pos+(0,0),np.random.random(2)*12-6,(0,1),self.explosion_anim_id,1,self.explosion_beha_id)
        