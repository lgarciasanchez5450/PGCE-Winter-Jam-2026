import typing

class TokenizingError(Exception): ...

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
                        out.append((text[i:ret],typ))
                    break
            else:
                raise TokenizingError
        return out
    
    
    