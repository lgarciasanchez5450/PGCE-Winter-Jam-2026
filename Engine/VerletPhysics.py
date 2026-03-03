import typing
from .Serialize import Writer, Reader,addSerializable

import numpy as np
import numpy.typing as npt


Vec2_NPCompat = tuple[float|np.floating,float|np.floating]|npt.NDArray[np.floating]

def serializeNDArray(writer:Writer,arr:np.ndarray):
    writer.write([int(s) for s in arr.shape])
    writer.writeStr(str(arr.dtype))
    writer.writeInt(arr.nbytes)
    writer.buf.extend(np.ascontiguousarray(arr).view(np.uint8))

def deserializeNDArray(reader:Reader) -> np.ndarray:
    shape = tuple(reader.readList(int))
    dtype = np.dtype(reader.readStr())
    buf_len = reader.readInt()
    
    buf = reader.buf[reader.i:reader.i+buf_len]
    reader.i += buf_len
    arr = np.frombuffer(buf,dtype)
    arr.shape = shape
    return arr

addSerializable(np.ndarray,serializeNDArray,deserializeNDArray)

class VerletPhysics:
    __slots__ = 'dt','capacity','size', 'pos','last_pos','id_to_ind','ind_to_id'
    def __init__(self,particles:int,dt:float):
        self.dt = dt
        self.capacity = particles
        self.size = particles
        self.pos = np.empty((self.capacity,2),np.float64) #sync dtypes to .deserialize method
        self.last_pos = np.empty((self.capacity,2),np.float64)
        self.id_to_ind = np.arange(self.capacity,dtype=np.intp)
        self.ind_to_id = np.arange(self.capacity,dtype=np.intp)
        
    def setPositions(self,pos:npt.NDArray[np.floating]|typing.Sequence[typing.Iterable[float]],sync_vel:bool=False):
        if sync_vel:
            dif = self.pos - self.last_pos
            self.pos[:] = pos  # type: ignore
            self.last_pos[:] = pos # type: ignore
            self.last_pos -= dif
        else:
            self.pos[:] = pos # type: ignore
            
    def setPosX(self,x:npt.NDArray[np.floating]|typing.Sequence[float]|float):
        self.pos[:,0] = x
    
    def setPosY(self,y:npt.NDArray[np.floating]|typing.Sequence[float]|float):
        self.pos[:,1] = y

    def getID(self,ind:typing.SupportsIndex) -> int:
        return self.ind_to_id[ind]

    def setVelocities(self,vel:npt.NDArray[np.floating]):
        self.last_pos[:] = self.pos
        self.last_pos[:self.size] -= vel * self.dt

    def getVels(self):
        dif = self.pos - self.last_pos
        dif /= self.dt
        return  dif[:self.size]
        
    def getPoss(self):
        return self.pos[:self.size]
    
    def getIDs(self):
        return self.ind_to_id[:self.size]

    def update(self,accel:npt.NDArray[np.float64]|None=None): 
        new_positions = 2*self.pos
        new_positions -= self.last_pos
        if accel is not None:
            new_positions[:self.size] += (accel * (self.dt*self.dt))
        self.last_pos = self.pos
        self.pos = new_positions

    def get(self,id:int):
        return self.pos[self.id_to_ind[id]]
    
    def gets(self,ids:typing.Sequence[int]|npt.NDArray[np.integer]):
        return self.pos[self.id_to_ind[ids]]

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

    @staticmethod
    def serialize(writer: Writer,self:'VerletPhysics'):
        writer.writeFloat(float(self.dt))
        writer.writeInt(int(self.capacity))
        writer.writeInt(int(self.size))
        writer.write(self.pos)
        writer.write(self.last_pos)
        writer.write(self.id_to_ind)
        writer.write(self.ind_to_id)
        
    @classmethod
    def deserialize(cls, reader: Reader) -> 'VerletPhysics':
        obj = VerletPhysics.__new__(VerletPhysics)
        dt = reader.readFloat()
        capacity = reader.readInt()
        size = reader.readInt()
        pos = reader.read(np.ndarray)
        last_pos = reader.read(np.ndarray)
        id_to_ind = reader.read(np.ndarray)
        ind_to_id = reader.read(np.ndarray)
        
        obj.dt = dt
        obj.capacity = capacity
        obj.size = size
        obj.pos = pos
        obj.last_pos = last_pos
        obj.id_to_ind = id_to_ind
        obj.ind_to_id = ind_to_id
        return obj
    
    def __eq__(self,other):
        if not isinstance(other,VerletPhysics): return False
        return bool((self.dt == other.dt) and (self.capacity == other.capacity) and (self.size == other.size) and \
            (np.all(self.pos==other.pos)) and (np.all(self.last_pos==other.last_pos)) and (np.all(self.id_to_ind==other.id_to_ind)) and (np.all(self.ind_to_id==other.ind_to_id)))

addSerializable(VerletPhysics,VerletPhysics.serialize,VerletPhysics.deserialize)