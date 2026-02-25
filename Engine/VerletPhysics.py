
import numpy as np
import numpy.typing as npt
import typing

T = typing.TypeVar('T',bound=np.float32|np.float64)

class VerletPhysics[T]:
    positions:npt.NDArray[T]
    def __init__(self,particles:int,dt:float):
        self.dt = dt
        self.positions = np.empty((particles,2),np.float32)
        self.last_positions = np.empty((particles,2),np.float32)

    def setVelocities(self,vel:npt.NDArray[np.float32]): ...
    
    def update(self):...
        

