from Engine import *
import time


def fade_out(screen:pygame.Surface,t:float):
    t_cur = time.perf_counter()
    t_end = t_cur+t
    surf = pygame.Surface(screen.size)
    while t_cur < t_end:
        dif = t_end-t_cur
        surf.set_alpha(int((1-dif)**2*255))
        screen.blit(surf)
        yield
        t_cur = time.perf_counter()
    surf.set_alpha(255)        
    screen.blit(surf)

def fade_in(screen:pygame.Surface,t:float):
    t_cur = time.perf_counter()
    t_end = t_cur + t
    surf = pygame.Surface(screen.size)
    while t_cur < t_end:
        dif = t_end-t_cur
        surf.set_alpha(int((dif)**2*255))
        screen.blit(surf)
        yield
        t_cur = time.perf_counter()
    surf.set_alpha(0)        
    screen.blit(surf)