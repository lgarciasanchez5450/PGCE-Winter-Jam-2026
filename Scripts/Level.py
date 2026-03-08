from Engine import *
from Scripts.Camera import Camera
from Scripts.MapDrawer import MapDrawer
from gameSim import GameState
import numpy as np

class Level(BaseSystem[GameState]):
    def getState(self) -> tuple[GameState]:
        return self.gamestate,
    
    def setState(self,gamestate:GameState):
        self.character_node = gamestate.start_node
        self.tick = 0
        self.connections = {(edge.a_node,edge.b_node):edge for edge in gamestate.edges}
        self.gamestate = gamestate
        self.possible_moves:list[int] = []
        self.move_option_i:int = 0

    def init(self):
        self.camera = self.engine.getSystem(Camera)
        self.map = self.engine.getSystem(MapDrawer)

        self.map.setMap(self.gamestate.nodes,self.gamestate.edges)
        

    def update(self):
        if self.engine.keys_down[pygame.K_SPACE]:
            self.onPlayerNodeChange()
            
        delta = self.engine.keys_down[pygame.K_RIGHT] - self.engine.keys_down[pygame.K_LEFT]
        if delta and self.possible_moves:
            self.move_option_i += delta
            self.move_option_i %= len(self.possible_moves)
            
        if self.engine.keys_down[pygame.K_z] and self.possible_moves:
            node_from = self.character_node
            node_to = self.possible_moves[self.move_option_i]
            dif = self.map.getPos(node_to) - self.map.getPos(node_from)
            move_angle = np.atan2(dif[1],dif[0])
            self.character_node = self.possible_moves[self.move_option_i]
            self.onPlayerNodeChange(keep_angle=move_angle)
        
    
    def draw(self):
        camera_offset = self.camera.offset
        character_pos = np.floor(self.map.getPos(self.character_node))
        
        self.engine.draw(
            Drawable.Rect('blue',pygame.Rect(0,0,20,20).move_to(center=character_pos).move(camera_offset),width=3),layer=3
        )
        for i,node in enumerate(self.possible_moves):
            color = 'green' if self.move_option_i == i else 'red'
            pos = np.floor(self.map.getPos(node))
            self.engine.draw(
                Drawable.Rect(color,pygame.Rect(0,0,20,20).move_to(center=pos).move(camera_offset),width=3),layer=3
            )
            
    def connection(self,a:int,b:int):
        if a>b: a,b = b,a
        return self.connections.get((a,b))
        
    def onPlayerNodeChange(self,keep_angle:float|None=None):

        self.possible_moves = self.possibleMoves(self.character_node)
        cur_pos = self.map.getPos(self.character_node)
        positions = self.map.world.gets(self.possible_moves)
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

        print(self.possible_moves)
            
    def possibleMoves(self,node:int) -> list[int]:
        out:list[int] = []
        for node in range(len(self.gamestate.nodes)):
            if node == self.character_node: continue
            edge = self.connection(self.character_node,node)
            if edge is None: continue
            if not edge.cycle[(self.tick+self.gamestate.start_tick)%len(edge.cycle)]: continue
            out.append(node)
        return out