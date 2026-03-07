import typing

class TokenizingError(Exception): ...
class UnexpectedTokenError(Exception): ...

class Tokenizer[T]:
    def __init__(self,grammar:dict[typing.Callable[[str,int],int],T|None]):
        self.grammar = grammar
        
    def tokenize(self,text:str) -> list[tuple[str,T]]:
        i = 0
        out:list[tuple[str,T]] = []
        while i < len(text):
            for f,typ in self.grammar.items():
                ret = f(text,i)
                if ret > 0:
                    if typ is not None:
                        out.append((text[i:i+ret],typ))
                    i += ret
                    break
            else:
                raise TokenizingError(f'Cannot tokenize from position: {text[i:i+20]}')
        return out
    
# tg_ : tokenize generic
def tg_Literal(literal:typing.LiteralString) -> typing.Callable[[str,int],int]:
    def _(s:str,i:int,literal=literal,length=len(literal)) -> int:
        if s[i:i+length] == literal:
            return length
        return 0
    return _

def t_decimal(s:str,i:int) -> int:
    k = 0
    while i+k < len(s) and s[i+k].isdecimal():
        k += 1
    return k

def t_hex(s:str,i:int) -> int:
    if s[i:i+2] != '0x':
        return 0
    k = 2
    while i+k < len(s) and (s[i+k].isdecimal() or s.lower() in 'abcdef'):
        k += 1
    return k

def t_whitespace(s:str,i:int) -> int:
    k = 0
    while i+k < len(s) and s[i+k].isspace():
        k += 1
    return k

def t_string(s:str,i:int) -> int:
    start = s[i]
    if start not in ('"','\''): return 0
    k = i+1
    while k < len(s) and s[k] != start:
        k+=1
        if s[k] == '\\':
            k+=1
    if k < len(s):
        return k-i+1
    return 0
    

type TokenType = typing.Literal[
    'PAREN_OPEN',
    'PAREN_CLOSE',
    'DECIMAL',
    'HEX',
    'COMMA',
    'STRING'
]

class LiteralParser:
    def __init__(self,s:str):
        self.s = s
        self.i = 0
        self.tokens = Tokenizer[TokenType](
            {
                tg_Literal('('):'PAREN_OPEN',
                tg_Literal(')'):'PAREN_CLOSE',
                tg_Literal(','):'COMMA',
                t_string:'STRING',
                t_decimal:'DECIMAL',
                t_hex:'HEX',
                t_whitespace:None
            }
        ).tokenize(s)
        
    def _getToken(self,i:int|None=None):
        if i is None: i = self.i
        return self.tokens[i]
    
    def ensureToken(self,*typs:TokenType):
        if self.tokens[self.i][1] not in typs:
            if len(typs) == 0:
                raise SyntaxError
            if len(typs) == 1:
                raise UnexpectedTokenError(f'Expected Token Type \'{typs[0]}\' got \'{self.tokens[self.i][1]}\'')
            else:
                raise UnexpectedTokenError(f'Expected Token Types {typs}\' got \'{self.tokens[self.i][1]}\'')
    def ensureNotToken(self,*typs:TokenType):
        if self.tokens[self.i][1] in typs:
            if len(typs) == 0:
                raise SyntaxError
            if len(typs) == 1:
                raise UnexpectedTokenError(f'Expected Not Token Type \'{typs[0]}\' got \'{self.tokens[self.i][1]}\'')
            else:
                raise UnexpectedTokenError(f'Expected Not Token Types {typs}\' got \'{self.tokens[self.i][1]}\'')

    def done(self):
        return self.i >= len(self.tokens)
        
    def consumeToken(self,*typs:TokenType):
        self.ensureToken(*typs)
        self.i += 1
        return self._getToken(self.i-1)
        
    def parseInt(self):
        s,typ = self._getToken(self.i)
        if typ == 'DECIMAL':
            self.i += 1
            return int(s)
        elif typ == 'HEX':
            self.i += 1
            return int(s[2:],base=16)
        else:
            raise UnexpectedTokenError
    
    def parseString(self):
        try:
            return self.consumeToken('STRING')[0][1:-1]
        except:
            raise
        
        
    def parseTuple(self) -> tuple:
        og_i = self.i
        try:
            self.consumeToken('PAREN_OPEN')
            if self._getToken()[1] == 'PAREN_CLOSE':
                return ()
            elements = [self.parse()]
            while self._getToken()[1] == 'COMMA':
                self.i += 1
                if self._getToken()[1] == 'PAREN_CLOSE':
                    break
                elements.append(self.parse())
            self.consumeToken('PAREN_CLOSE')            
            return tuple(elements)
        finally:
            self.i = og_i

    
    def parse[T](self) -> T:
        for f in [self.parseTuple,self.parseInt,self.parseString]:
            try:
                return f()
            except:
                pass
        raise Exception
            
            
if __name__ == '__main__':
    
    pass
    cases:dict[str,typing.Any] = {
        '1':1,
        '99':99,
        '31':31,
        '()':(),
        '(1,)':(1,),
        '(1,2)':(1,2),
        '"Hello!"':'Hello!',
        "'Hello!'":'Hello!'
    }
    passed = 0
    failed:list[tuple[str,typing.Any]] = []
    for test,answer in cases.items():
        try:
            obj = LiteralParser(test).parse()
        except Exception as err:
            failed.append((test,err))
        else:
            if obj == answer:
                passed += 1
            else:
                failed.append((test,obj))
    print(f'{passed} Successful Tests')
    print(f'{len(failed)} Failing Tests')
    for test,obj in failed:
        print('Failed Test:',test,'->',repr(obj))
        