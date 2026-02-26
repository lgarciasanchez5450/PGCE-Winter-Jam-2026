
import numpy as np
import numpy.typing as npt
import typing

Vec2_NPCompat = tuple[float|np.floating,float|np.floating]|npt.NDArray[np.floating]

T = typing.TypeVar('T',bound=np.floating)

class VerletPhysics:
    __slots__ = 'dt','capacity','size', \
        'pos','last_pos','id_to_ind','ind_to_id'
    def __init__(self,particles:int,dt:float):
        self.dt = dt
        self.capacity = particles
        self.size = particles
        self.pos = np.empty((self.capacity,2),np.float64)
        self.last_pos = np.empty((self.capacity,2),np.float64)
        self.id_to_ind = np.arange(self.capacity,dtype=np.intp)
        self.ind_to_id = np.arange(self.capacity,dtype=np.intp)
        
    def setPositions(self,pos:npt.NDArray[T],sync_vel:bool=False):
        if sync_vel:
            dif = self.pos - self.last_pos
            self.pos[:] = pos
            self.last_pos[:] = pos
            self.last_pos -= dif
        else:
            self.pos[:] = pos

    def setVelocities(self,vel:npt.NDArray[np.floating]):
        self.last_pos[:] = self.pos
        self.last_pos -= vel * self.dt

    def update(self,accel:npt.NDArray[np.float64]): 
        new_positions = 2*self.pos
        new_positions -= self.last_pos
        new_positions += accel * (self.dt*self.dt)
        self.pos = new_positions
        self.last_pos = self.pos

    def remove(self,id:int):
        self.size -= 1
        i_last = self.size
        i = self.id_to_ind[id]
        
        self.pos[i] = self.pos[i_last]
        self.last_pos[i] = self.last_pos[i_last]
        
        id_of_last = self.ind_to_id[i_last]
        id_of_removed = id
        
        self.ind_to_id[i] = id_of_last
        self.ind_to_id[i_last] = id_of_removed
        
        self.id_to_ind[id_of_last] = i
        self.id_to_ind[id_of_removed] = i_last

    def append(self,pos:Vec2_NPCompat,vel:Vec2_NPCompat) -> int:
        index = self.size
        self.size += 1
        if self.size > self.capacity:
            self.inflate()
        id = self.ind_to_id[index]

        self.id_to_ind[id] = index
        self.ind_to_id[index] = id
        
        self.pos[index] = pos
        self.last_pos[index] = pos
        self.last_pos[index] -= np.array(vel) * self.dt
        return id
        
    def inflate(self):
        new_capacity = max(self.capacity,1)
        while self.size > new_capacity:
            new_capacity *= 2
        pos = np.empty((new_capacity,2),np.float64)
        last_pos = np.empty((new_capacity,2),np.float64)
        id_to_ind = np.arange(new_capacity,dtype=np.intp)
        ind_to_id = np.arange(new_capacity,dtype=np.intp)
        
        pos[:self.capacity] = self.pos
        last_pos[:self.capacity] = self.last_pos
        id_to_ind[:self.capacity] = self.id_to_ind
        ind_to_id[:self.capacity] = self.ind_to_id
        
        self.pos = pos
        self.last_pos = last_pos
        self.id_to_ind = id_to_ind
        self.ind_to_id = ind_to_id
        self.capacity = new_capacity
