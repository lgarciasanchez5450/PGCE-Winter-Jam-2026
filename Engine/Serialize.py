import typing
import types

T = typing.TypeVar('T')
TC = typing.TypeVar('TC',bound=typing.Callable)
trtable:dict[str,type] = {}
twtable:dict[type,str] = {}
wtable = {}
rtable = {}
DEBUG = True
def w(typ:type[T]):
    addSerializableType(typ,typ.__name__)
    def _(func:TC) -> TC:
        if DEBUG:
            def wrapper(r:'Writer',t=None,f=func):
                start = len(r.buf)
                r.debug_i += 1
                out = f(r,t)
                r.debug_i -= 1
                end = len(r.buf)
                if r.debug_i == 0:
                    r.debug.append((end-start,typ.__name__))
                return out
            func = wrapper#type: ignore

        wtable[typ] = func
        return func
    return _

def r(typ):
    def _(func:TC) -> TC:
        if func.__code__.co_argcount == 1:
            if DEBUG:
                def wrapper(r:'Reader',t=None,f=func):
                    start = r.i
                    r.debug_i += 1
                    out = f(r)
                    r.debug_i -= 1
                    end = r.i
            
                    if r.debug_i == 0:
                        r.debug.append((end-start,typ.__name__))
                    return out
                func = wrapper#type: ignore
            rtable[typ] = lambda s,t:func(s)
                
        elif func.__code__.co_argcount == 2:
            if DEBUG:
                def wrapper(r:'Reader',t=None,f=func):
                    start = r.i
                    r.debug_i += 1
                    out = f(r,t)
                    r.debug_i -= 1
                    end = r.i
            
                    if r.debug_i == 0:
                        r.debug.append((end-start,typ.__name__))
                    return out
                func = wrapper#type: ignore
            rtable[typ] = func
        else:
            raise NotImplementedError
        return func
    return _


def addSerializableType(typ:type,name:str|None=None):
    name = name if name is not None else typ.__name__
    if name in trtable: raise NameError(f'Error Registering Type {repr(typ.__name__)}, Name {repr(name)} already maps to type {repr(trtable[name])}')
    if typ in twtable: raise TypeError(f'Error Registering Type {repr(typ.__name__)}, Type {repr(typ)} already maps to name {repr(twtable[typ])}')
    trtable[name] = typ
    twtable[typ] = name
    
def addSerializable(typ:type[T],ser:typing.Callable[['Writer',T],typing.Any],deser:typing.Callable[['Reader'],T]):
    if (typ in wtable) or (typ in rtable): raise TypeError(f'Type {repr(typ.__name__)} already is serializable.')
    wtable[typ] = ser
    # r(typ)(deser)
    rtable[typ] = lambda s,t,f=deser:f(s)
    try:
        addSerializableType(typ)
    except (NameError, TypeError):
        pass

def isSerializeable(obj:typing.Any) -> bool:
    typ = type(obj)
    if typ in wtable:
        if typ in (set,tuple,list):
            return all(map(isSerializeable,obj))
        return True
    return False

class Writer:
    def __init__(self):
        self.buf = bytearray()
        if __debug__:
            self.debug:list[tuple[int,str]] = []
            self.debug_i = 0
            
    def printDebug(self):
        if not __debug__: return
        a = ' '+bytes(self.buf).hex(' ')
        out = '|'
        for l,n in self.debug:
            sl = l*3-1
            if sl > len(n):
                out += f'{n.center(sl)}|'
            elif l > 0:
                
                out += f'{n[-sl:]}|'
            else:
                out += ''
                
        line_width = 200
        while len(a) > line_width:
            print(a[:line_width])
            print(out[:line_width])
            a = a[line_width:]
            out = out[line_width:]


        
    @w(int)
    def writeInt(self,x:int):
        b = bytearray()
        neg = x < 0
        if neg: x = -x
        while x:
            v = x&0xFF
            b.append(v|0b10000000)
            x >>= 7
        b.reverse()
        self.buf.extend(b)
        self.buf.append(neg)
    
    @w(type(None))
    def writeNone(self):
        return
        
    @w(bool)
    def writeBool(self,b:bool):
        if b:
            self.buf.append(1)
        else:
            self.buf.append(0)
            
    @w(bytes)
    def writeBytes(self,b:typing.Collection[int]):
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
      
    @w(type)
    def writeType(self,typ:type):
        self.writeStr(twtable[typ])
            
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
        if __debug__:
            self.debug:list[tuple[int,str]] = []
            self.debug_i = 0    
            
    def printDebug(self):
        if not __debug__: return
        print(' '+bytes(self.buf).hex(' '))
        out = '|'
        for l,n in self.debug:
            sl = l*3-1
            if sl > len(n):
                out += f'{n.center(sl)}|'
            elif l > 0:
                
                out += f'{n[-sl:]}|'
            else:
                out += ''
        print(out)
            
    @r(int)   
    def readInt(self):
        x = 0
        v = 0
        while self.i < len(self.buf) and (v:=self.buf[self.i]) & 0b10000000:
            x <<= 7
            x |= v & 0b01111111
            self.i+=1
        if v:
            x = -x
        self.i+=1
        return x
    
    @r(bool)
    def readBool(self):
        if self.i >= len(self.buf): return False
        out = bool(self.buf[self.i])
        self.i += 1
        return out
    
    @r(type(None))
    def readNone(self):
        return None
    
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
            d = self.readInt() or 1
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
        
    @r(type)
    def readType(self):
        return trtable[self.readStr()]

        
    @property
    def done(self): return self.i >= len(self.buf)
    
    def read(self,typ:type[T]) -> T:
        if typ in rtable:
            return rtable[typ](self,typ)
        typ_typ = type(typ)
        if typ_typ in rtable: 
            return rtable[typ_typ](self,typ)
        raise NotImplementedError


