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

class GLIndexBufferObject:
    
    def __init__(self, window:Window):
        self.window = window
        self.mVBO = glGenBuffers(1)
    
    def __del__(self):
        self.dispose()
    
    def dispose(self):
        if self.mVBO == None:
            return
        if self.window.active():
            glDeleteBuffers(1, [self.mVBO])
        self.mVBO = None
    
    def upload(self, data, sizeBytes, draw_type = GL_STATIC_DRAW):
        """GL_STATIC_DRAW, GL_DYNAMIC_DRAW"""
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.mVBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeBytes, data, draw_type)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    
    def setIndex(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.mVBO)
    
    def drawIndex(primitive, count, type, offset):
        glDrawElements(primitive, count, type, offset)
    
    def unsetIndex():
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
