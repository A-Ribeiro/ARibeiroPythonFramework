#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
from OpenGL.GL import *
from aRibeiro.window import *

class GLVertexArrayObject:
    
    def __init__(self, window:Window):
        self.window = window
        self.mVAO = glGenVertexArrays(1)
    
    def __del__(self):
        self.dispose()
    
    def dispose(self):
        if self.mVAO == None:
            return
        if self.window.active():
            glDeleteVertexArrays(1, [self.mVAO])
        self.mVAO = None
    
    def enable(self):
        glBindVertexArray(self.mVAO)

    def disable(self):
        glBindVertexArray(0)
    
    def drawIndex(primitive, count, type, offset):
        glDrawElements(primitive,count,type,offset)
    
    def drawArrays(primitive, count, offset):
        glDrawArrays(primitive, offset, count)
