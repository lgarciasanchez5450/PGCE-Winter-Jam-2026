import typing
import types

T = typing.TypeVar('T')
TC = typing.TypeVar('TC',bound=typing.Callable)

wtable = {}
rtable = {}
def w(typ:type[T]):
    def _(func:typing.Callable[[typing.Any,T],typing.Any]):
        wtable[typ] = func
        return func
    return _

def r(typ):
    def _(func:TC) -> TC:
        if func.__code__.co_argcount == 1:
            rtable[typ] = lambda s,t:func(s)
        elif func.__code__.co_argcount == 2:
            rtable[typ] = func
        else:
            raise NotImplementedError
        return func
    return _

class Writer:
    def __init__(self):
        self.buf = bytearray()
 
        
    @w(bool)
    def writeBool(self,b:bool):
        if b:
            self.buf.append(1)
        else:
            self.buf.append(0)
            
    @w(bytes)
    def writeBytes(self,b:bytes):
        self.writeInt(len(b))
        self.buf.extend(b)
    
    w(bytearray)(writeBytes)
            
    @w(str)
    def writeStr(self,s:str):
        self.writeBytes(s.encode('utf-8'))
    
    @w(float)
    def writeFloat(self,f:float):
        try:
            n,d = f.as_integer_ratio()
        except OverflowError: #
            self.buf.append(1)
            self.writeBool(f > 0)
        except ValueError:
            self.buf.append(2)
        else:
            self.buf.append(0)
            self.writeInt(n)
            self.writeInt(d)
            
    
    def writeIterable(self,iter:typing.Iterable):
        for item in iter:
            self.write(item)
            
    def writeSizedIterable(self,iter:typing.Collection):
        self.writeInt(len(iter))
        self.writeIterable(iter)
            
    w(tuple)(writeIterable)
    w(list)(writeSizedIterable)
    w(set)(writeSizedIterable)
    
    
    def length(self):
        return len(self.buf)
            
    def write(self,x:typing.Any):
        typ = type(x)
        if typ in wtable:
            wtable[typ](self,x)
        else:
            raise NotImplementedError
        
class Reader:
    def __init__(self,buf:bytes|bytearray) -> None:
        self.buf = buf
        self.i = 0
    
    @r(int)   
    def readInt(self):
        x = 0
        while self.i < len(self.buf) and (v:=self.buf[self.i]):
            x <<= 7
            x |= v & 0b01111111
            self.i+=1
        self.i+=1
        return x
    
    @r(bool)
    def readBool(self):
        if self.i >= len(self.buf): return False
        out = bool(self.buf[self.i])
        self.i += 1
        return out
    
    @r(bytes)
    def readBytes(self):
        len = self.readInt()
        out = self.buf[self.i:self.i+len]
        self.i += len
        return out
    
    @r(str)
    def readStr(self):
        return self.readBytes().decode('utf-8')
    
    @r(float)
    def readFloat(self):
        if self.i >= len(self.buf): return float('nan')
        v = self.buf[self.i]
        self.i += 1
        if v == 0:
            n = self.readInt()
            d = self.readInt()
            return n/d
        elif v== 1:
            positive = self.readBool()
            if positive:
                return float('inf')
            else:
                return -float('inf')
        else:
            return float('nan')
    
    def readIterable(self,types:typing.Iterable[type[T]]) -> typing.Iterable[T]:
        for typ in types:
            out = self.read(typ)
            yield out
    @r(tuple)
    def readTuple(self,types:tuple[type]) -> tuple:
        return tuple(self.readIterable(types))
    @r(list)
    def readList(self,typ:type[T]) -> list[T]:
        size = self.readInt()
        return [x for x in self.readIterable((typ,)*size)]
    @r(set)
    def readSet(self,typ:type[T]) -> set[T]:
        size = self.readInt()
        return set(self.readIterable((typ,)*size))
    
    @r(types.GenericAlias)
    def readGenericAlias(self,g_alias:types.GenericAlias):
        typ = g_alias.__origin__
        args = g_alias.__args__
        
        if typ is list or typ is set:
            args = args[0]
        return rtable[typ](self,args)
        
    @property
    def done(self): return self.i >= len(self.buf)
    
    def read(self,typ:type[T]) -> T:
        if typ in rtable:
            return rtable[typ](self,typ)
        typ_typ = type(typ)
        if typ_typ in rtable: 
            return rtable[typ_typ](self,typ)
        raise NotImplementedError
