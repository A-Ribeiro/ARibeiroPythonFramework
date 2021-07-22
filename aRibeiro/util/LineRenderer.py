#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
import numpy as np
from aRibeiro.math import *
from aRibeiro.opengl import *
#from multiprocessing import RLock
from threading import RLock
# threading.get_ident() works, or threading.current_thread().ident (or threading.currentThread().ident for Python < 2.6).
from aRibeiro.window import *

class LineRenderer:
    def __init__(self, window:Window, line_width = 1.5):
        self.window = window
        self.line_width = line_width
        self.shader = PositionColorShader(window)
        self.vertex_line_pos = np.array([],dtype=np.float32)
        self.vertex_line_color = np.array([],dtype=np.float32)
        self.lock = RLock()
    def __del__(self):
        self.dispose()
    def dispose(self):
        self.shader.dispose()
    
    def clear(self):
        self.lock.acquire()
        self.vertex_line_pos = np.resize(self.vertex_line_pos, 0) #np.array([],dtype=np.float)
        self.vertex_line_color = np.resize(self.vertex_line_color, 0) #np.array([],dtype=np.float)
        self.lock.release()

    def addLine(self, 
        vertex_a, 
        vertex_b, 
        color_a = np.array([1,0,1,1],dtype=np.float32),
        color_b = np.array([1,1,0,1],dtype=np.float32)):

        self.lock.acquire()
        self.vertex_line_pos = np.append(self.vertex_line_pos, vertex_a)
        self.vertex_line_pos = np.append(self.vertex_line_pos, vertex_b)
        self.vertex_line_color = np.append(self.vertex_line_color, color_a)
        self.vertex_line_color = np.append(self.vertex_line_color, color_b)
        self.lock.release()

    
    def draw(self, mvpMatrix:np.array, auto_clear:bool = True):
        if np.size(self.vertex_line_pos) == 0:
            return
        
        self.lock.acquire()
        vertex_count = np.floor_divide( np.size(self.vertex_line_pos), 3 )
        #print("Drawing", np.floor_divide(vertex_count,2), "lines")

        glLineWidth(self.line_width)

        self.shader.enable()
        self.shader.setMVP_Matrix4x4(mvpMatrix)
        #self.shader.setMVP_Matrix4x4(self.projection)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, float_size(3), self.vertex_line_pos)

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 4, GL_FLOAT, False, float_size(4), self.vertex_line_color)

        glDrawArrays(GL_LINES, 0, vertex_count )

        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(0)

        if auto_clear:
            self.clear()

        self.lock.release()
