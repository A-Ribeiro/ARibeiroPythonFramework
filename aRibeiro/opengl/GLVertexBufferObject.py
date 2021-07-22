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

class GLVertexBufferObject:
    
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
        glBindBuffer(GL_ARRAY_BUFFER, self.mVBO)
        glBufferData(GL_ARRAY_BUFFER, sizeBytes, data, draw_type)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    def setLayout(self, layoutIndex, sizeCount, type, strideBytes, offset):
        glBindBuffer(GL_ARRAY_BUFFER, self.mVBO)
        glVertexAttribPointer(layoutIndex, sizeCount, type, GL_FALSE, strideBytes, offset)
        glEnableVertexAttribArray(layoutIndex)
    
    def unsetLayout(self, layoutIndex):
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableVertexAttribArray(layoutIndex)

    def drawArrays(primitive, count, offset):
        glDrawArrays(primitive, offset, count)
