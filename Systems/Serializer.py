import typing
import types

# from System import BaseSystem

T = typing.TypeVar('T')
TC = typing.TypeVar('TC',bound=typing.Callable)

class BytesLike(typing.Protocol):
    # def __setitem__(self, key:int, value:int): ...
    def __getitem__(self, key:int) -> int: ...
    def __iter__(self) -> typing.Iterator[int]: ...
    def __buffer__(self,flags:int,/) -> memoryview: ...
    def __len__(self) -> int: ...
    

class SIZE(int):
    def serialize(self,meta:BytesLike|bytes|bytearray=b'') -> bytes:
        a = int(self)
        b = bytearray()
        while a:
            x = a&0xFF
            b.append(x|0b10000000)
            a >>= 7
        b.reverse()
        for m in meta:
            if m&0b10000000:
                raise ValueError('Metadata byte cannot have MSB set')
            if m==0:
                raise ValueError('Metadata cannot use reserved byte \\x00')
        b.extend(meta)            
        b.append(0)
        return bytes(b)
    
    @staticmethod
    def deserialize(b:bytes|memoryview) -> 'tuple[int,bytearray,int]':
        l = 0
        x = 0
        m = bytearray()
        while v:=b[l]:
            flag = v >> 7
            v = v & 0b01111111
            if flag:
                x <<= 7
                x |= v
            else:
                m.append(v)
            l+=1
        return x,m,l+1

class Serializer:
    def __init__(self) -> None:
        self.s:dict[type,typing.Callable] = {}
        self.ds:dict[int,typing.Callable] = {}
        self.type_to_id:dict[type,int] = {}
        self.id_to_type:dict[int,type] = {}
        
    def registerDefaults(self):
        def w(typ):
            def _(func):
                self.s[typ] = func
                return func
            return _
        
        def r(typ):
            def _(func):
                self.ds[typ] = func
                return func
            return _

        @w(bool)
        def sBool(b:bool):
            return b'\1' if b else b'\0',
        
        def dsBool(b:bytes) -> bool:
            return bool(int.from_bytes(b))
    
    
        def sInt(i:int):
            return i.to_bytes(i.bit_length()//8,signed=True)
        def dsInt(b:bytes):
            return int.from_bytes(b,signed=True) 
        
        # def sBytes(b:bytes):
        #     return b
        # def dsBytes()
        

        
        def sFloat(f:float) -> bytes:
            try:
                num,den = f.as_integer_ratio()
            except OverflowError: #is inf
                pass
            except ValueError: #is nan
                pass
            return b''
        def dsFloat(b:bytes) -> float:
            return 0.0
        self.registerSerializable(float,sFloat,dsFloat)
        
    def registerSerializable(self,cls:type[T],serializer:typing.Callable[[T],bytes],deserializer:typing.Callable[[bytes|memoryview],T]):
        id = len(self.type_to_id)+1
        self.type_to_id[cls] = id
        self.id_to_type[id] = cls
        self.s[cls] = serializer
        self.ds[id] = deserializer
    
    def getSerializer(self,cls:type[T]) -> typing.Callable[[T],bytes]:
        return self.s[cls]

    
    def getDeserializer(self,id:int) -> typing.Callable[[bytes|memoryview],object]:
        return self.ds[id]
    
    def pack(self,*b:bytes) -> bytes:
        out = bytearray()
        for bytes_ in b:
            out.extend(SIZE(len(bytes_)).serialize())
            out.extend(bytes_)
        return bytes(out)
        
    def unpack(self,b:bytes|BytesLike) -> list[memoryview]:
        out:list[memoryview] = []
        i = 0
        buf = b.__buffer__(0)
        while i < len(b):
            size,_,l = SIZE.deserialize(buf[i:])
            i += l
            out.append(buf[i:i+size])
            i += size
        return out
        
    def serialize(self,obj:T): #type: ignore
        typ = type(obj)
        type_id = self.type_to_id[typ]
        serializer = self.getSerializer(typ)
        serialized = serializer(obj)
        serialized_len = len(serialized)
        return b''.join([
            SIZE(type_id).serialize(),
            SIZE(serialized_len).serialize(),
            serialized
        ])
        
    def deserialize(self,b:memoryview|bytes) -> object:
        i = 0
        view = memoryview(b).toreadonly()
        type_id,_,l = SIZE.deserialize(view[i:])
        i += l
        serialized_len,_,l = SIZE.deserialize(view[i:])
        i += l
        deserializer = self.getDeserializer(type_id)
        return deserializer(view[i:i+serialized_len])
        
    def update(self): ...
    def draw(self): ...
    

wtable:dict = {}
rtable:dict = {}
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
        
    @w(int)
    def writeInt(self,x:int):
        b = bytearray()
        while x:
            x = x&0xFF
            b.append(x|0b10000000)
            x >>= 7
        b.reverse()
        self.buf.extend(b)
        self.buf.append(0)
        
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
    
    @w(type)
    def writeType(self,typ):
        id = [bool,int,float,str,bytes,list,set,tuple,bytearray].index(typ)
        self.writeInt(id)  
        
        
    
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
            # print('reading type:',typ.__name__)
            out = self.read(typ)
            # print('out:',out)
            yield out
            # yield self.read(typ)
    @r(tuple)
    def readTuple(self,types:tuple[type]) -> tuple:
        # print('reading tuple',types)
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
        else:
            typ_typ = type(typ)
            return rtable[typ_typ](self,typ)
        raise NotImplementedError

writer = Writer()
writer.write(1.0)
writer.write(False)
writer.write('hello!')
writer.write([1,2,3])
writer.write(('hello',1,2.0,False))
print(writer.buf)
print(writer.length())
# writer.write((0,False))
# b'\1\0'
# writer.write(True)
# b'\1\0\1'
# writer.write(object)
# b'\1\0\1'
reader = Reader(bytes(writer.buf))
print(reader.read(float))
print(reader.read(bool))
print(reader.read(str))
print(reader.read(list[int]))
print(reader.read(tuple[str,int,float,bool]))