from Engine import *
import typing
import numpy as np
import numpy.typing as npt

type Vec2Like = tuple[float,float]|typing.Sequence[float]|npt.NDArray

def _check_valid_animation(anim:list[pygame.Surface]):
    if not anim:
        raise ValueError(f'Empty Animation')
    size = anim[0].size
    for frame in anim:
        if frame.size != size:
            raise OverflowError(f'All frames of a single particle animation must have same size, not {[f.size for f in anim]}')

class Bucket:
    __slots__ = 'i','size','pos','vel','accel','anim_id','anim_len','frame','fps','behav_id','alive'
    def __init__(self,size:int):
        self.size = size
        self.i = 0
        self.pos = np.empty((size,2),np.float32)
        self.vel = np.empty((size,2),np.float32)
        self.accel = np.empty((size,2),np.float32)
        self.anim_id = np.empty(size,np.uint32)
        self.anim_len = np.empty(size,np.int32)
        self.frame = np.empty(size,np.float32)
        self.fps = np.empty(size,np.float32)
        self.behav_id = np.empty(size,np.uint32)
        self.alive = np.zeros(size,np.bool)

class ArrayProxy[T:npt.NDArray]:
    __slots__ = 'array','mask'
    def __init__(self,array:T,mask:npt.NDArray[np.bool]):
        self.array = array
        self.mask = mask
    def mask_(self,v):
        if type(v) in (int,float):
            return v
        return v[self.mask]    
    
    def __iadd__(self,other:npt.NDArray):
        other = self.mask_(other)
        self.array[self.mask] += other
        return self
    def __isub__(self,other:npt.NDArray):
        other = self.mask_(other)
        self.array[self.mask] -= other
        return self
    def __imul__(self,other:npt.NDArray):
        other = self.mask_(other)
        self.array[self.mask] *= other
        return self
    def __itruediv__(self,other:npt.NDArray):
        other = self.mask_(other)
        self.array[self.mask] /= other
        return self
    def __ifloordiv__(self,other:npt.NDArray):
        other = self.mask_(other)
        self.array[self.mask] //= other
        return self
    def __imod__(self,other:npt.NDArray):
        other = self.mask_(other)
        self.array[self.mask] %= other
        return self

    def __setitem__(self, key:tuple[slice|int,...]|slice, value:npt.NDArray):
        if isinstance(key,tuple):
            first,*other = key
            new_mask = np.zeros_like(self.mask,dtype=np.bool)
            new_mask[first] = True
            new_mask &= self.mask
            self.array[new_mask,*other] = value[self.mask]
        elif isinstance(key,np.ndarray):
            new_mask = np.logical_and(self.mask,key)
            self.array[new_mask] = value
        else:
            if not (key.start or key.stop or key.step):
                self.array[self.mask] = value[self.mask]
            else:
                new_mask = np.zeros_like(self.mask,dtype=np.bool)
                new_mask[key] = True
                new_mask &= self.mask
                self.array[new_mask] = value[self.mask]
                
    def __getitem__(self,key):
        return self.array.__getitem__(key)
    
    def __add__(self,other) -> T:
        return self.array + other
    
    __radd__ = __add__
    
    def __sub__(self,other:npt.NDArray):
        return self.array - other 
    
    __rsub__ = __add__
    
    def __mul__(self, other) -> T:
        return self.array * other
    
    __rmul__ = __mul__
    
    def __gt__(self,other):
        if isinstance(other,ArrayProxy):other = other.array
        return self.array > other
    
    def __ge__(self,other):
        if isinstance(other,ArrayProxy):other = other.array
        return self.array >= other
    
    def __lt__(self,other):
        if isinstance(other,ArrayProxy):other = other.array
        return self.array < other
    
    def __le__(self,other):
        if isinstance(other,ArrayProxy):other = other.array
        return self.array <= other
        
    
class BucketProxy:
    __slots__ = 'pos','vel','accel','anim_id','anim_len','frame','fps','behav_id','alive'
    def __init__(self,bucket:Bucket,mask:npt.NDArray[np.bool]):
        self.pos = ArrayProxy(bucket.pos,mask)
        self.vel = ArrayProxy(bucket.vel,mask)
        self.accel = ArrayProxy(bucket.accel,mask)
        self.anim_id = ArrayProxy(bucket.anim_id,mask)
        self.anim_len = ArrayProxy(bucket.anim_len,mask)
        self.frame = ArrayProxy(bucket.frame,mask)
        self.fps = ArrayProxy(bucket.fps,mask)
        self.behav_id = ArrayProxy(bucket.behav_id,mask)
        self.alive = ArrayProxy(bucket.alive,mask)
        
class Particles:
    def __init__(self):
        self.buckets:list[Bucket] = []
        self.anim_offst = np.zeros((0,2),np.int32)
        self.anim_len = np.zeros(0,np.int32)
        self.anims:list[list[pygame.Surface]] = []
        self.behaviours:list[typing.Callable[[Bucket,npt.NDArray[np.bool]],typing.Any]] = [lambda *_:None]
        self.layer = 0
        self._last_i = 0

        
    def update(self,dt:float):
        i = 0
        
        while i < len(self.buckets):
            b = self.buckets[i]
            if b.i:
                if self._last_i < i+1:
                    self._last_i = i+1
                behaviours = np.unique(b.behav_id[b.alive]) #TODO: slow
                for behaviour_id in behaviours:
                    behaviour = self.behaviours[int(behaviour_id)]
                    behaviour(b,b.behav_id==behaviour_id)
                    
                if not np.any(b.alive): 
                    b.i = 0
                    
                b.pos += b.vel * dt
                b.vel += b.accel * dt
                b.frame += b.fps * dt
            i += 1
        self._last_i = 0
        
    def draw(self,surf:pygame.Surface,offset:tuple[int,int]):

        for b in self.buckets:
            pos = np.floor(b.pos)[b.alive].astype(np.int32) + offset
            anim_ids = b.anim_id[b.alive]
            pos += self.anim_offst[anim_ids]
            frame = b.frame.astype(np.int32)
            frame %= b.anim_len
            
            surf.fblits([(self.anims[anim_id][frame],pos) for anim_id,frame,pos in zip(anim_ids,frame,pos)])
            
    def setLayer(self,layer:int):
        self.layer = layer
 
    @property
    def animCount(self): return len(self.anims)

    def addAnimation(self,anim:list[pygame.Surface]) -> int:
        _check_valid_animation(anim)
        if self.animCount == len(self.anim_offst):
            new_size = max(2*len(self.anim_offst),1)
            self.anim_offst.resize((new_size,2))
            self.anim_len.resize(new_size)

        anim_id = self.animCount        
        size = anim[0].size
        self.anim_offst[anim_id] = (-size[0]//2,-size[1]//2)
        self.anim_len[anim_id] = len(anim)
        self.anims.append(anim.copy())
        return anim_id

    def setAnimation(self,anim_id:int,anim:list[pygame.Surface]):
        _check_valid_animation(anim)
        if anim_id >= self.animCount:
            raise KeyError(f'Invalid Animation ID {anim_id}')
        
        size = anim[0].size
        self.anim_offst[anim_id] = (-size[0]//2,-size[1]//2)
        self.anim_len[anim_id] = len(anim)
        self.anims[anim_id] = anim.copy()
        
    def addBehaviour(self,behaviour:typing.Callable[[Bucket,npt.NDArray[np.bool]],typing.Any]) -> int:
        self.behaviours.append(behaviour)
        return len(self.behaviours) - 1
        
    def addParticle(self,pos:Vec2Like,vel:Vec2Like,accel:Vec2Like,anim_id:int,fps:float,behaviour_id:int):
        while self._last_i < len(self.buckets):
            bucket = self.buckets[self._last_i]
            if bucket.i < bucket.size:
                break
            self._last_i += 1
        else:
            self._last_i = len(self.buckets)
            size = 1<<len(self.buckets)
            bucket = Bucket(size)
            self.buckets.append(bucket)

        i = bucket.i
        bucket.pos[i] = pos
        bucket.vel[i] = vel
        bucket.accel[i] = accel
        bucket.anim_id[i] = anim_id
        bucket.anim_len[i] = self.anim_len[anim_id]
        bucket.frame[i] = 0
        bucket.fps[i] = fps
        bucket.behav_id[i] = behaviour_id
        bucket.alive[i] = True
        bucket.i += 1