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

class GLRenderBuffer:
    def __init__(self, window:Window, width, height, internalformat = GL_DEPTH_COMPONENT24):
        self.window = window
        self.width = width
        self.height = height
        self.format = internalformat
        #self.mRenderbuffer = GLuint()
        self.mRenderbuffer = glGenRenderbuffers(1)
        self.enable()
        self.setSize(width, height, internalformat)
        self.disable()
        self.is_depth_stencil = internalformat != GL_DEPTH_COMPONENT16 and internalformat != GL_DEPTH_COMPONENT24 and internalformat != GL_DEPTH_COMPONENT32
    def __del__(self):
        self.dispose()
    def dispose(self):
        if self.mRenderbuffer == None:
            return
        if self.window.active():
            glDeleteRenderbuffers(1, [self.mRenderbuffer])
        self.mRenderbuffer = None
    def enable(self):
        glBindRenderbuffer(GL_RENDERBUFFER, self.mRenderbuffer)
    def disable(self):
        glBindRenderbuffer(GL_RENDERBUFFER, 0)
    def setSize(self, width, height, internalformat = GL_DEPTH_COMPONENT24):
        glRenderbufferStorage(GL_RENDERBUFFER, internalformat, width, height)

