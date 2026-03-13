
def ident(t:float) -> float: return t

def smoothstep(t:float) -> float:
    t2 = t*t
    t3 = t2*t
    return 3*t2 - 2*t3

def square(t:float): return t*t

def cube(t:float): return t*t*t

def sqrt(t:float): return t**0.5

def cbrt(t:float): return t**(1/3)
