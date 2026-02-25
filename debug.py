if __name__ == '__main__':
    #We use a lot of introspection that relies on this invariant
    raise RuntimeError('The Debug module cannot be run directly!')
import typing
import sys
import math
import numpy as np
from time import perf_counter
from functools import partial
from numpy.typing import NDArray
from numba import njit

@njit
def to_ext_array(nodes:NDArray,children:NDArray[np.uint32],i:int,ofst:int):
    node = nodes[i]
    child = node[3]
    if child:
        og_ofst = ofst
        children[ofst] = child
        ofst += 1
        while nodes[child][4] != 0:
            child = nodes[child][4]
            children[ofst] = child
            ofst += 1
        node[3] = og_ofst
        node[4] = ofst-og_ofst
        for child_i in children[og_ofst:ofst]:
            ofst = to_ext_array(nodes,children,child_i,ofst) #type: ignore
    else:
        node[3] = 0
        node[4] = 0
    return ofst

@njit
def to_linked_list(nodes:NDArray[np.void],children:NDArray[np.uint32],i):
    #in place operation,
    #this changes the meaning of ofst and children of each node, to first_child & next_sibling respectively
    node = nodes[i]
    ofst = node[3]
    knum = node[4]
    kid_array = children[ofst:ofst+knum]
    if i == 0:
        nodes[0][4] = 0
    prev = -2
    if kid_array.size: #this node has children
        child_index = 999
        for child_index in kid_array:
            to_linked_list(nodes,children,child_index)  #have to do kids first because we overwrite the data
            if prev == -2:
                nodes[i][3] = child_index
            else:
                nodes[prev][4] = child_index
            prev = child_index
        #we need to fix the next_sibling of the last sibling because it doesnt exist so we make it reference 0
        nodes[child_index][4] = 0
    else:
        nodes[i][3] = 0 #if it doesnt have any children set its child to 0

@njit
def parseNode(raw_trace:NDArray,node_i:int,out_data:NDArray,out_i:int) -> int:
    node = raw_trace[node_i]

    out_node = out_data[out_i]
    out_node[0] = node[0]
    out_node[1] = node[1]
    out_node[2] = 1

    next_i = node_i + 1
    if next_i == raw_trace.size:
        return 1

    next = raw_trace[next_i]
    next_parent_i = next[2]
    if next_parent_i == node_i:
        out_node[3] = out_i + 1 #set curent nodes first child to be this next node
        stride = parseNode(raw_trace,next_i,out_data,out_i+1)
        last_sibling = out_i + 1
        next_i += stride
        out_i += stride
    else:
        return 1
    while next_i < raw_trace.size:
        next = raw_trace[next_i]
        next_parent_i = next[2]
        if next_parent_i == node_i:
            out_data[last_sibling][4] = out_i+1
            stride = parseNode(raw_trace,next_i,out_data,out_i+1)
            last_sibling = out_i + 1
            next_i += stride
            out_i += stride
        else:
            break
    return next_i - node_i


T_CALLABLE = typing.TypeVar('T_CALLABLE',bound=typing.Callable)
T_TYPE = typing.TypeVar('T_TYPE',bound=type)


class Timer:
    __slots__ = 'time','t_start'

    def start(self):
        self.t_start = perf_counter()

    def stop(self):
        self.time = perf_counter() - self.t_start

    def __enter__(self):
        self.t_start = perf_counter()
        return self

    def __exit__(self,exc_type,exc_val,traceback):
        self.time = perf_counter() - self.t_start
        return False

    def format(self) -> str:
        return fTime(self.time,3,2)


class Tracer:
    __slots__ = 'i','i2','cur','reset_node','id_to_fqn','raw_trace','__dict__','malloc_id'
    def __init__(self):
        self.max_can_trace = (2<<16)-1
        self.reset_node = None
        self.id_to_fqn:list[str] = []
        self.root_id = self.register_id('__root__')
        self.malloc_id = self.register_id('<DEBUG OVERHEAD>: Memory Allocation')
        self.used_buckets:list[np.ndarray] = []
        self.bucket_size = 1_000_000
        self.bytes_per_time = 4

        self.dtype = np.dtype([('id', np.uint16), ('time',np.float32),('parent',np.int32)])
        self.expanded_dtype = np.dtype([('id',np.uint16),('time',np.float32),('ncalls',np.uint32),('ofst',np.uint32),('children',np.uint32)])
        self.raw_trace = np.empty(self.bucket_size,self.dtype)
        print('Bucket Byte Size:',self.raw_trace.nbytes,'bytes')
        self.i = 0
        self.i2 = 0
        self.cur_i = -1
        self.notes_by_uuid:dict[int,str] = {}

    def register_id(self,fqn:str):
        if len(self.id_to_fqn) ==  self.max_can_trace: raise RuntimeError(f'Cannot Trace More than {self.max_can_trace} functions')
        self.id_to_fqn.append(sys.intern(fqn))
        return len(self.id_to_fqn) - 1


    @staticmethod
    def notrace(func:T_CALLABLE) -> T_CALLABLE:
        func.__doc__ = 'Tracing Function Wrapper'
        return func
    
    @notrace
    def trace(self,func:T_CALLABLE, func_name=None,fqn = None) -> T_CALLABLE:
        if getattr(func,'__doc__',None) == 'Tracing Function Wrapper': return func
        if not fqn:
            fqn = getattr(func,'__qualname__',func_name or func.__name__)
            module_name = getattr(func,'__module__',None)
            if module_name:
                fqn = module_name + ':'+ fqn

        fqn_id = self.register_id(fqn)

        is_static = type(func) is staticmethod
        is_classm = type(func) is classmethod
        if is_static or is_classm:
            func = func.__func__ #type: ignore
        def wrapper(*args,__func__=func,__tracer__:Tracer=self,__tmr__=perf_counter,__fqn_id__=fqn_id,**kwargs):
            parent_index = __tracer__.cur_i
            i = __tracer__.i
            i2 = __tracer__.i2
            __tracer__.i += 1
            __tracer__.i2 += 1
            start = __tmr__()
            raw_trace = __tracer__.raw_trace
            try:
                if __tracer__.i == __tracer__.bucket_size:
                    _start = __tmr__()
                    __tracer__.used_buckets.append(__tracer__.raw_trace)
                    __tracer__.i = 1
                    __tracer__.i2 += 1
                    __tracer__.raw_trace = np.empty(__tracer__.bucket_size,__tracer__.dtype)
                    __tracer__.raw_trace[0][0] = __tracer__.malloc_id
                    __tracer__.raw_trace[0][2] = i2
                    __tracer__.raw_trace[0][1] = __tmr__() - _start
                __tracer__.cur_i = i2
                return __func__(*args,**kwargs)
            finally:
                raw_trace[i][0] = __fqn_id__
                raw_trace[i][2] = parent_index
                __tracer__.cur_i = parent_index
                raw_trace[i][1] = __tmr__() - start
                
        wrapper.__doc__ = 'Tracing Function Wrapper'
        wrapper.__name__ = func.__name__
        wrapper.__annotations__ = getattr(func,'__annotations__',None) #type: ignore
        if is_static:
            return staticmethod(wrapper) #type: ignore
        elif is_classm:
            return classmethod(wrapper) #type: ignore
        return wrapper #type: ignore
    
    @notrace
    def traceas(self,func_name=None,fqn=None):
        return partial(self.trace,func_name=func_name,fqn=fqn)
    
    @notrace
    def dprint(self,*values,sep:str=' ',end='\n'):
        return print('dprint does not work at this time.')
        s = sep.join([str(v) for v in values]) + end
        try:
            self.cur.notes += s
        except AttributeError:
            self.cur.notes = s
    
    @notrace
    def show(self): #runs a program to see what happened
        import pygame as pg
        print('Function Calls Traced:',self.i2)
        print('Runtime Memory Footprint:',fMem((len(self.used_buckets) + 1) * self.raw_trace.nbytes,4,3))
        if self.i2 == 0:
            print('No Functions Traced! Quitting.')
            return



        raw_trace = np.empty(self.i2,self.dtype)
        i = 0
        for bucket in self.used_buckets:
            raw_trace[i:i+bucket.size] = bucket
            i += bucket.size
        raw_trace[i:] = self.raw_trace[:self.i]
        if self.reset_node is not None and self.reset_node != 0:
            i = self.reset_node
            while i < raw_trace.size and raw_trace[i][2] != -1:
                i += 1
            raw_trace = raw_trace[i:].copy()
            for node in raw_trace:
                node[2] -= i
        if raw_trace.size == 0:
            print('No Calls traced after last Reset! Quitting.')
            return


        WIN = pg.Window('Debug Trace',resizable=True)
        def cache1(func):
            cache_key = None
            cache_value = None
            def wrapper(*args,**kwargs):
                nonlocal cache_key, cache_value
                key = args + tuple([kwargs[k] for k in sorted(kwargs.keys())])
                if key != cache_key:
                    cache_key = key
                    cache_value = func(*args,**kwargs)
                return cache_value
            return wrapper
        @cache1
        def render_multiline(font:pg.Font,string:str,aa:bool,color:pg.typing.ColorLike,wraplen:int=0,bgcolor:pg.typing.ColorLike=(0,0,0,0),padding:int=0) -> pg.Surface:
            renders = [font.render(line,aa,color,wraplength=wraplen) for line in string.splitlines()]
            out = pg.Surface((max(map(pg.Surface.get_width,renders))+ padding*2,sum(map(pg.Surface.get_height,renders))+padding*2),pg.SRCALPHA)
            out.fill(bgcolor)
            y = padding
            for render in renders:
                out.blit(render,(padding,y))
                y += render.height
            return out


        #we have to convert all the little stuffs
        def iter_children(nodes:NDArray,i):
            first_child_i = nodes[i][3]
            #check if valid child
            if first_child_i == 0: return
            yield first_child_i
            yield from iter_siblings(nodes,first_child_i)


        def next_sibling(nodes:NDArray,i:int) -> int:
            return nodes[i][4]

        def iter_siblings(nodes:NDArray[np.void],i:int):
            #yields all sibling nodes following the current one
            while True:
                next_sibling_i = nodes[i][4]
                if next_sibling_i == 0: break
                yield next_sibling_i
                i = next_sibling_i

        def convert_from_raw():
            node_data = np.zeros(self.i2+1,self.expanded_dtype) #fqn_id, time, ncalls, first_child, next_sibling
            root_time = raw_trace[0][1]
            stride = parseNode(raw_trace,0,node_data,1)
            last_frame = 1
            node_i = stride
            while node_i < raw_trace.size:
                root_time += raw_trace[node_i][1]
                stride = parseNode(raw_trace,node_i,node_data,node_i + 1)
                node_data[last_frame][4] = node_i + 1
                last_frame = node_i + 1
                node_i += stride
            node_data[0] = (self.root_id,root_time,1,1,0)
            #convert from linked list to use external array
            children = np.empty(self.i2,np.uint32)
            to_ext_array(node_data,children,0,0)
            return node_data,children


        def convert_from_raw_selecting_frames(frames:set[int]):
            node_i = 0
            out_i = 1
            frame = 0
            while frame not in frames:
                node_i += 1
                while node_i < raw_trace.size and raw_trace[node_i][2] != -1:
                    node_i += 1
                frame += 1
            frames.remove(frame)
            node_data = np.zeros(self.i2+1,self.expanded_dtype) #fqn_id, time, ncalls, first_child, next_sibling
            root_time = raw_trace[node_i][1]
            stride = parseNode(raw_trace,node_i,node_data,out_i)
            last_frame = 1
            frame += 1
            node_i += stride
            out_i += stride
            while frames:
                #advance node_i to next valid frame
                while frame not in frames:
                    node_i += 1
                    while raw_trace[node_i][2] != -1:
                        node_i += 1
                    frame += 1
                frames.remove(frame)
                frame += 1
                root_time += raw_trace[node_i][1]
                stride = parseNode(raw_trace,node_i,node_data,out_i)
                node_data[last_frame][4] = out_i
                last_frame = out_i
                out_i += stride
                node_i += stride

            node_data[0] = (self.root_id,root_time,1,1,0)
            #convert from linked list to use external array
            children = np.empty(self.i2,np.uint32)
            to_ext_array(node_data,children,0,0)
            return node_data,children


        nodes,children = convert_from_raw()

        print('Node Representation Memory:',fMem(nodes.nbytes + children.nbytes,3,2))

        root_subcalls:list[tuple[str,float]] = []
        _,_,_,ofst,kids = nodes[0]
        for index in children[ofst:ofst+kids]:
            id,time,_,_,_ = nodes[index]
            root_subcalls.append((
                self.id_to_fqn[id],
                float(time)
            ))
                    
        def format_linked(nodes:NDArray,i:int=0) -> str:
            fqn_id,time,n_calls,first_child,_ = nodes[i]
            fqn_id:int
            children_formated = [format_linked(nodes,child_i) for child_i in iter_children(nodes,i)]
            out_l = []
            if children_formated:
                for child_f in children_formated[:-1]:
                    child_f_splitlines = child_f.splitlines()
                    t = '├─' + child_f_splitlines[0] + '\n'
                    for line in child_f_splitlines[1:]:
                        t += '│ ' + line + '\n'
                    out_l.append(t)
                child_f_splitlines = children_formated[-1].splitlines()
                t = '└─' + child_f_splitlines[0] + '\n'
                for line in child_f_splitlines[1:]:
                    t += '  ' + line + '\n'
                out_l.append(t)

            return f'{self.id_to_fqn[fqn_id].split(':',1)[-1]}\n{''.join(out_l)}'
            # '─│┌┐└┘├┤┬┴┼'
            
        @njit#(boundscheck=True)
        def _collapse(nodes:NDArray[np.void],i):
            child_i = nodes[i][3]
            while child_i:
            # for child_i in iter_children(nodes,i):
                fqn_id = nodes[child_i][0]
                childs_child_i = nodes[child_i][3]
                # fqn_id,time,ncalls,childs_child_i,_ = nodes[child_i]
                if childs_child_i:
                    next_ = nodes[childs_child_i][4]
                    while next_:
                        childs_child_i = next_
                        next_ = nodes[childs_child_i][4]

                prior_sibling_to_next_i = child_i
                next_sibling_i = nodes[prior_sibling_to_next_i][4]
                while next_sibling_i:
                    #check if equal or not 
                    next_sibling_ = nodes[next_sibling_i]
                    if next_sibling_[0] == fqn_id:
                        nodes[child_i][1] += next_sibling_[1]
                        nodes[child_i][2] += next_sibling_[2]
                        nodes[prior_sibling_to_next_i][4] = next_sibling_[4]
                        if childs_child_i:
                            nodes[childs_child_i][4] = nodes[next_sibling_i][3]
                        else:
                            childs_child_i = nodes[child_i][3] = nodes[next_sibling_i][3]
                        next_ = nodes[childs_child_i][4]
                        while next_:
                            childs_child_i = next_
                            next_ = nodes[childs_child_i][4]
                    else:
                        prior_sibling_to_next_i = next_sibling_i
                    next_sibling_i = nodes[prior_sibling_to_next_i][4]
                child_i = nodes[child_i][4]
            child_i = nodes[i][3]
            while child_i:
                _collapse(nodes,child_i)
                child_i = nodes[child_i][4]

        def collapse(nodes:NDArray[np.void],children:NDArray[np.uint32]): #in-place
            to_linked_list(nodes,children,0) #in-place
            _collapse(nodes,0)
            to_ext_array(nodes,children,0,0)
            
        def sort(nodes:NDArray,children:NDArray[np.uint32],reverse:bool=False,i:int=0):
            #in-place
            def getTime(x):
                return nodes[x][1]
            node = nodes[i]
            ofst = node[3]
            knum = node[4]
            children[ofst:ofst+knum] = sorted(children[ofst:ofst+knum],key=getTime,reverse=reverse)
            for child_i in children[ofst:ofst+knum]:
                sort(nodes,children,reverse,child_i)


        def fqn_to_color(fqn:str) -> pg.Color:
            h = hash(fqn)
            hue =  (h>>8)%360
            sat = (h&0xFF)%50+50
            val = h%20+80
            return pg.Color.from_hsva(hue,sat,val) #type: ignore
        pg.font.init()
        pg.key.set_repeat(400,50)
        font = pg.font.SysFont('Arial',13)
        big_font = pg.font.SysFont('Arial',20)
        font_mono = pg.font.SysFont('monospace',15)

        fqn_surf_cache:dict[int,pg.Surface] = {}
        search_for:None|str = None
        searching:bool = False

        def draw(surf:pg.Surface,nodes,children,rect_height,offset_x,offset_y,xmul,ymul,min_width,max_children):
            if max_children < 0: max_children = float('inf')
            multiplier = WIN.size[0] / float(nodes[0][1]) * xmul
            rect_height *= ymul
            surf_width,surf_height = surf.get_size()

            def draw_children(nodes,children,node_i:int,rect:pg.FRect):
                if rect.right < 0: return
                if rect.y >= surf_height: return
                if rect.w < min_width: return
                fqn_id, time,ncalls,ofst,len_ = nodes[node_i]
                if rect.bottom > 0:
                    fqn = self.id_to_fqn[fqn_id]
                    if search_for and search_for not in fqn:
                        color = (100,100,100)
                    else:
                        color = fqn_to_color(fqn) 

                    pg.draw.rect(surf,color,rect)
                    if rect.width >= min_width + 5:
                        if (fqn_surf:=fqn_surf_cache.get(fqn_id)) is None:
                            fqn_surf = fqn_surf_cache[fqn_id] = font.render(fqn,True,0)

                        surf.blit(fqn_surf,rect)
                        parent_notes = ''#self.notes_by_uuid.get(parent.uuid,'')
                        lines = parent_notes.splitlines()
                        #we have a few cases for rendering the node notes
                        if 2*font.size(parent_notes)[1] > rect.height: #there is no space below title, render aligned to the right
                            notes_surf = font.render(parent_notes.replace('\n',''),True,0)
                            surf.blit(notes_surf,notes_surf.get_rect(topright=rect.topright))
                        elif lines:
                            surfs = [font.render(l,True,0) for l in lines]
                            start_y = font.size(fqn)[1]
                            cum_width = 0
                            max_cur_width = 0
                            cum_height = start_y
                            for lsurf in surfs:
                                if cum_height + lsurf.get_height() > rect.height:
                                    cum_height = start_y
                                    cum_width += max_cur_width + 5 #some spacing so it looks nice
                                    max_cur_width = 0
                                surf.blit(lsurf,rect.move(cum_width,cum_height))
                                max_cur_width = max(max_cur_width,lsurf.get_width())
                                cum_height += lsurf.get_height()+2

                child_rect = pg.FRect(rect.x,rect.bottom,0,rect_height)
                for child_i in children[ofst:ofst+min(len_,max_children)]:
                    child = nodes[child_i]
                    child_rect.width = float(child[1])*multiplier
                    if child_rect.left >= surf_width: break
                    draw_children(nodes,children,child_i,child_rect)
                    child_rect.x += child_rect.w
            draw_children(nodes ,children,0,pg.FRect(0,0,float(nodes[0][1])*multiplier,rect_height).move(offset_x,offset_y))

        def draw_details(surf:pg.Surface,rect_height,offset_x,offset_y,xmul,ymul,mpos:tuple[int,int]):
            nonlocal show_percents
            root_time = float(nodes[0][1])
            multiplier = WIN.size[0] / root_time * xmul
            rect_height *= ymul
            def draw_details_(node_i:int,rect:pg.FRect,mpos:tuple[int,int]):
                if rect.top > mpos[1]: return
                if rect.w < 1: return False
                fqn_id, time,n_calls,ofst,len_ = nodes[node_i]
                fqn_id:int
                if rect.collidepoint(mpos):
                    fqn = self.id_to_fqn[fqn_id]
                    cumtime = time
                    tottime = max(0,cumtime - sum(nodes[child_i][1] for child_i in children[ofst:ofst+len_]))
                    if show_percents:
                        lines = [
                            f'Name: {fqn.split(':',1)[1] if ':' in fqn else fqn}',
                            f'Module: {fqn.split(':',1)[0]}' if ':' in fqn else '',
                            f'Details: [% Mode] (%\'s of Cumulative Root Time)',
                            f'  Times: Cumulative | Exclude Sub-Calls | N-Calls ',
                            f'          {100*cumtime/root_time:>8.2f}% |     {100*tottime/root_time:>8.2f}%     |{n_calls:^8}'
                        ] #l+3+n+1 = 3+3+2+1 = 9

                    else:    
                        lines = [
                            f'Name: {fqn.split(':',1)[1] if ':' in fqn else fqn}',
                            f'Module: {fqn.split(':',1)[0]}' if ':' in fqn else '',
                            f'Details:',
                            f'  Times: Cumulative | Exclude Sub-Calls | N-Calls ',
                            f'          {fTime(cumtime,3,2)} |     {fTime(tottime,3,2)}     |{n_calls:^8}'
                        ]

                    text = '\n'.join(list(filter(bool,lines)))
                    surf2 = render_multiline(font_mono,text,True,0,0)
                    rect = surf2.get_frect(topleft = mpos)
                    rect.clamp_ip(surf.get_rect())
                    pg.draw.rect(surf,'gray',rect,0,2)
                    surf.blit(surf2,rect)
                    return True

                x = rect.x
                for child_i in children[ofst:ofst+len_]:
                    child = nodes[child_i]
                    child_rect = pg.FRect(x,rect.bottom,float(child[1])*multiplier,rect_height)
                    if child_rect.left > mpos[0]: break
                    if not (child_rect.right < mpos[0]):
                        if draw_details_(child_i,child_rect,mpos): return True
                    x += child_rect.w
                return False
            return draw_details_(0,pg.FRect(0,0,root_time*multiplier,rect_height).move(offset_x,offset_y),mpos)
        running = True
        clock = pg.time.Clock()
        offset = pg.Vector2([0,0])
        mult = pg.Vector2([0,0])
        screen = WIN.get_surface()
        frames_still = 0
        frame = 0
        collapsing_frames = [big_font.render(f'{'-\\|/'[i]} Collapsing...',True,'white') for i in range(4)]
        help = '''Modifiers:
L-CTRL  - Vertical 
L-SHIFT - Horizontal 
L-SHIFT - Reverse Sort
Keycodes:
R - Reset Frame
ESC - Quit Search
ENTER - Save Search
ALT+F - Select Frames
ALT+C - Collapse
ALT+S - Sort By Time
ALT+P - Toggle % Times
CTRL+F - Search
'''
        help2 = '''Modifiers:
L-CTRL  - Vertical 
L-SHIFT - Horizontal 
Keycodes:
R - Reset Frame
ESC - Cancel
ALT+ENTER - Accept
'''
        setting_to = None
        help_surf = render_multiline(font,help,True,'white',bgcolor=(50,50,50),padding=3)
        help_hint = render_multiline(font,'TAB - Help',True,'white',bgcolor=(0,0,0,100),padding=2)
        help_surf2 = render_multiline(font,help2,True,'white',bgcolor=(50,50,50),padding=3)
        show_percents = False

        state = 'icicle'
        def icicle_menu(events:list[pg.Event]):
            nonlocal frames_still,mult,offset,state,fps,show_percents,searching,search_for
            m_press = pg.mouse.get_pressed()
            rel = pg.Vector2(pg.mouse.get_rel())
            if rel == (0,0):
                frames_still += 1
            else:
                frames_still = 0
            rel *= m_press[0]

            mpos = pg.mouse.get_pos()
            keys = pg.key.get_pressed()
            kd = pg.key.get_just_pressed()
            dmult = pg.Vector2([wheel,wheel])
            #Check for state transitions
            if not searching:
                if kd[pg.K_f] and (keys[pg.K_LCTRL] or keys[pg.K_RCTRL]):
                    searching = True

                if keys[pg.K_LALT] or keys[pg.K_RALT]:
                    if kd[pg.K_f]:
                        state = 'pick frames'
                        fps = 120
                        mult.update()
                        offset.update()
                        pg.mouse.set_visible(True)
                        return

                    if kd[pg.K_c]:
                        collapse(nodes,children)

                    if kd[pg.K_s]:
                        reverse = keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]
                        sort(nodes,children,reverse)
                    
                    if kd[pg.K_p]:
                        show_percents = not show_percents

                if kd[pg.K_r]:
                    dmult -= mult
                    rel -= offset
            elif kd[pg.K_ESCAPE]:
                searching = False
                search_for:str|None = None
            elif kd[pg.K_RETURN]:
                searching = False
            else:
                key_events = [event for event in events if event.type == pg.KEYDOWN]
                if key_events:
                    for key_event in key_events:
                        if key_event.key == pg.K_BACKSPACE:
                            if key_event.mod&pg.KMOD_CTRL:
                                search_for = None
                            else:
                                if search_for is not None:
                                    search_for = search_for[:-1]
                        else:
                            if search_for is None:
                                search_for = key_event.unicode
                            else:
                                search_for += key_event.unicode


            if not (keys[pg.K_LCTRL] ^ keys[pg.K_LSHIFT]):
                mult += dmult
                offset += rel
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            else:
                if keys[pg.K_LSHIFT]:
                    pg.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZEWE)
                if keys[pg.K_LCTRL]:
                    pg.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZENS)
                mask = pg.Vector2(keys[pg.K_LSHIFT],keys[pg.K_LCTRL])
                dmult = dmult.elementwise() * mask
                mult += dmult
                offset += rel.elementwise() * mask
            if dmult and not kd[pg.K_r]:
                offset[0] = 2**(dmult[0]/10) * (offset[0] - mpos[0]) + mpos[0]
                offset[1] = 2**(dmult[1]/10) * (offset[1] - mpos[1]) + mpos[1]
            #Draw Stuff
            screen.fill(0)
            draw(screen,nodes,children,30,offset[0],offset[1],2**(mult[0]/10),2**(mult[1]/10),0.5,-1)
            
            if frames_still > 30 :
                pg.mouse.set_visible(not draw_details(screen,30,offset[0],offset[1],2**(mult[0]/10),2**(mult[1]/10),mpos))
            else:
                pg.mouse.set_visible(True)
            if searching:
                width = WIN.size[0] * 0.3
                height = font.point_size
                text = None
                if search_for:
                    text = font.render(search_for,False,'white')
                    if text.width > width:
                        width = text.width
                rect = pg.Rect(0,0,width,height)
                rect.centerx = int(screen.width * 0.5)
                rect.centery = int(screen.height * 0.85)
                pg.draw.rect(screen,(60,60,60),rect.inflate(6,6),3)
                if search_for and text:
                    screen.blit(text,rect)

            if not searching and keys[pg.K_TAB]:
                screen.blit(help_surf,help_surf.get_rect(topright=(screen.width,0)))
            else:
                screen.blit(help_hint,help_hint.get_rect(topright=(screen.width,0)))


        def pick_menu(frame_indices_picked:set = set()):
            nonlocal setting_to,fps,mult,offset,state,nodes,children,show_percents
            keys = pg.key.get_pressed()
            kd = pg.key.get_just_pressed()
            screen.fill(0)
            rect_height = 20
            mpres = pg.mouse.get_pressed()
            mpresd = pg.mouse.get_just_pressed()
            mpos = pg.mouse.get_pos()

            #Detect State Transition
            if keys[pg.K_LALT] and kd[pg.K_RETURN]:
                #do the stuff
                nodes,children = convert_from_raw_selecting_frames(frame_indices_picked.copy(),)
                mult.update()
                offset.update()
                state = 'icicle'
                return
            elif kd[pg.K_ESCAPE]:
                frame_indices_picked.clear()
                mult.update()
                offset.update()
                state = 'icicle'
                return

            if kd[pg.K_r]:
                a = not (keys[pg.K_LSHIFT] ^ keys[pg.K_LCTRL])
                mask = a or pg.Vector2(keys[pg.K_LSHIFT],keys[pg.K_LCTRL])
                mult -= mult.elementwise() * mask
                offset -= offset.elementwise() * mask
            if not (keys[pg.K_LSHIFT] ^ keys[pg.K_LCTRL]):
                offset[1] += wheel * rect_height
            else:
                mask = pg.Vector2(keys[pg.K_LSHIFT],keys[pg.K_LCTRL])
                dmult = mask * wheel
                min_height_per_box = (screen.height - 40) / len(root_subcalls)
                dmult[1] = max(dmult[1],math.log(min_height_per_box/rect_height,2)*10-mult[1])
                mult += dmult


                if wheel and not kd[pg.K_r]:
                    offset[1] = 2**(dmult[1]/10) * (offset[1] - mpos[1]) + mpos[1]
            width_multiplier = 2**(mult[0]/10) * screen.width/2/(root_subcalls[0][1])
            height_multiplier = 2**(mult[1]/10)

            offset[1] = max(offset[1],(screen.height-20)-rect_height * height_multiplier*len(root_subcalls))
            offset[1] = min(offset[1],20)

            y = offset[1]
            for i,(node_fqn,node_time) in enumerate(root_subcalls):
                width = node_time * width_multiplier
                height = rect_height * height_multiplier
                if y + height < 0:
                    y += height
                    continue
                rect = pg.Rect((offset[0],y,width,height))
                is_picked = i in frame_indices_picked
                if mpresd[0]:
                    if rect.collidepoint(mpos):
                        setting_to = not is_picked
                        if setting_to:
                            frame_indices_picked.add(i)
                        elif is_picked:
                            frame_indices_picked.remove(i)
                elif mpres[0]:
                    if rect.collidepoint(mpos):
                        if setting_to:
                            frame_indices_picked.add(i)
                        elif is_picked:
                            frame_indices_picked.remove(i)
                color = fqn_to_color(node_fqn)
                if not is_picked:
                    color = color.grayscale()
                pg.draw.rect(screen,color,rect)
                name_surf = font.render(node_fqn.split(':')[-1],True,'black')
                screen.blit(name_surf,(offset[0],y))
                time_surf = font.render(fTime(node_time,3,2),True,'black')
                if width - name_surf.width > time_surf.width:
                    screen.blit(time_surf,(offset[0]+width-time_surf.get_width(),y))
                y += height
                if y > screen.height: break

            if keys[pg.K_TAB]:
                screen.blit(help_surf2,help_surf2.get_rect(topright=(screen.width,0)))
            else:
                screen.blit(help_hint,help_hint.get_rect(topright=(screen.width,0)))

        fps = 60
        while running:
            frame += 1
            wheel:int = 0
            events = pg.event.get()
            for event in events:
                if event.type == pg.WINDOWCLOSE:
                    running = False
                if event.type == pg.MOUSEWHEEL:
                    wheel += event.precise_y #type: ignore
            if state == 'icicle':
                icicle_menu(events)
            elif state == 'pick frames':
                pick_menu()

            WIN.flip()
            clock.tick(fps)
    
    @notrace
    def traceClass(self,class_:T_TYPE) -> T_TYPE:
        for attr_name in dir(class_):
            if attr_name.startswith('__'): continue
            attr = class_.__dict__[attr_name]
            if callable(attr) and type(attr) is not type:
                setattr(class_,attr_name,self.trace(attr))
        return class_
    
    @notrace
    def traceModule(self,globals_:dict[str,typing.Any],outermost_path:str,do_not_trace:typing.Iterable|None=None,_modules_traced:set|None=None):
        import sys,os
        outermost_path = os.path.abspath(outermost_path)
        if _modules_traced is None: _modules_traced = set()

        builtin_modules = set(sys.builtin_module_names) | set(['os','abc','st','path'])
        do_not_trace = set(do_not_trace or [])
        do_not_trace.update([Tracer,sys.modules[__name__],self.trace,self.traceas,self.dprint,self.show,trace,traceas,dprint,show,traceModule],)
        for key,value in globals_.items():
            if key.startswith('__'): continue
            try:
                if value in do_not_trace: continue
            except TypeError: pass
            if type(value) is type(sys): #if its a module
                pass
            elif type(value) is type and value is not type: #if its a class
                try:
                    globals_[key] = self.traceClass(value)
                except Exception: pass
            elif callable(value): #if its a module-wide function
                globals_[key] = self.trace(value)

        for module_name,module in sys.modules.items():
            if module in do_not_trace: continue
            if module_name in _modules_traced: continue
            _modules_traced.add(module_name)
            if not (getattr(module,'__file__','') or '').startswith(outermost_path): continue
            if module_name in builtin_modules: continue
            if module_name.startswith('_'): continue
            self.traceModule(module.__dict__,outermost_path,do_not_trace,_modules_traced)
            
    @notrace
    def reset(self):
        self.reset_node = self.i2


def fTime(t:float,l:int,n:int):
    #The length of this string will be at least l + 3 [+ n + 1] minus the part in brackets if n == 0
    if t:
        i = 0
        while t < 1 and i < 3:
            t *= 1000
            i += 1
    else:
        i = -1

    suffix = [' s ',' ms',' µs',' ns'] #always length of 3
    int_ = int(t)
    frac = int((t % 1) * 10**n)
    if n != 0:   # l               + 1 +      n                + 3
        return str(int_).rjust(l) + '.' + str(frac).ljust(n) + suffix[i]
    else:
        return str(int_).rjust(l) + suffix[i]

def fMem(b:float,l:int,n:int,type_:typing.Literal['bytes','bits'] = 'bytes'):
    if b < 0: raise ValueError('Negative Bytes Makes no sense!')
    i = 0
    while b > 1024:
        b /= 1024
        i += 1
    suffix = ['  ',' Ki',' Mi',' Gi',' Ti',' Pi',' Ei'][i] + {'bytes':'B','bits':'bs'}[type_]
    int_ = int(b)
    frac = int((b%1) * 10**n)

    if n != 0:
        return str(int_).rjust(l) + '.' + str(frac).ljust(n,'0') + suffix
    else:
        return str(int_).rjust(l) + suffix

def profile(func=None,show_args=False):
    if func is None:
        return partial(profile,show_args=show_args)
    def _(*args,**kwargs):
        s = perf_counter()
        v = func(*args,**kwargs)
        e = perf_counter()
        if show_args:
            s_args = [repr(arg) for arg in args]
            s_args.extend([f'{k}={repr(v)}' for k,v in kwargs.items()])
            print(f'{func.__name__}({', '.join(s_args)}): {(e-s)*1000:.2f} ms')
        else:
            print(f'{func.__name__}: {(e-s)*1000:.2f} ms')
        return v
    _.__name__ = func.__name__
    return _
        
def profileResursive(func=None,show_args=False):
    if func is None:
        return partial(profileResursive,show_args=show_args)
    stack = 0
    def _(*args,**kwargs):
        nonlocal stack
        stack += 1
        s = perf_counter()
        v = func(*args,**kwargs)
        e = perf_counter()
        stack -= 1
        if stack==0:
            if show_args:
                s_args = [repr(arg) for arg in args]
                s_args.extend([f'{k}={repr(v)}' for k,v in kwargs.items()])
                print(f'{func.__name__}({', '.join(s_args)}): {(e-s)*1000:.2f} ms')
            else:
                print(f'{func.__name__}: {(e-s)*1000:.2f} ms')
        return v
    _.__name__ = func.__name__
    return _



TRACER = Tracer()
#Module-wide aliases to simplify use
def trace(func): return TRACER.trace(func)
def traceas(func_name=None,fqn=None):return TRACER.traceas(func_name,fqn)
def show(): return TRACER.show()
def dprint(*values,sep=' ',end='\n'): return TRACER.dprint(*values,sep=sep,end=end)
def traceClass(class_:T_TYPE) -> T_TYPE: return TRACER.traceClass(class_)
def traceModule(globals_:dict,outermost_path): return TRACER.traceModule(globals_,outermost_path)
def reset(): return TRACER.reset()