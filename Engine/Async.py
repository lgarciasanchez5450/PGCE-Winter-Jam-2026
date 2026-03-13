import typing
import types
import time

T = typing.TypeVar('T')
T2 = typing.TypeVar('T2')

class Coro(typing.Protocol):
    def __next__(self): ...
    def __iter__(self) -> 'Coro': ...

class WaitFrames:
    __slots__ = 'left','err'
    def __init__(self,frames:int):
        self.left = frames
        self.err = StopIteration
        
    def __await__(self):
        self.err = StopAsyncIteration
        return self
    
    def __next__(self):
        self.left -= 1
        if self.left <= 0:
            raise self.err       
        
    def __iter__(self):
        return self 

class WaitTime:
    __slots__ = 'end','err','timer','len'
    def __init__(self,end:float,timer:typing.Callable[[],float],len):
        self.timer = timer
        self.end = end
        self.len = len
        self.err = StopIteration
        
    @property
    def countdown(self):
        return max(0,(self.end - self.timer() )/ self.len)
        
    @classmethod
    def untilTime(cls,end:float):
        return cls(end,time.perf_counter,end-time.perf_counter())
    
    @classmethod
    def forSeconds(cls,duration:float):
        return cls(time.perf_counter()+duration,time.perf_counter,duration)
        
    def __await__(self):
        self.err = StopAsyncIteration
        return self
    
    def __next__(self):
        if time.perf_counter() >= self.end:
            raise self.err

    def __iter__(self):
        return self


class Context:
    __slots__ = 'coros',
    def __init__(self):
        self.coros:dict[typing.Any,typing.Generator] = {}
        
    def add(self,coro:typing.Generator):
        if await_ := getattr(coro,'__await__',None):
            gen = await_()
        else:
            gen = coro
        self.coros[coro] = gen
        
    def isAlive(self,coro:typing.Generator):
        return coro  in self.coros

    def remove(self,coro:typing.Generator):
        self.coros.pop(coro)
        
    def tick(self):
        self.coros = {k:v for k,v in self.coros.items() if self.tickCoro(v)}
    
    def tickCoro(self,coro:typing.Generator):
        try:
            coro.__next__()
        except StopIteration:
            return False
        else:
            return True
        
    
    @staticmethod
    def run(gen:typing.Generator[typing.Any,typing.Any,T]) -> tuple[T]:
        while True:
            try:
                gen.__next__()
            except StopIteration as err:
                return err.value
        
                