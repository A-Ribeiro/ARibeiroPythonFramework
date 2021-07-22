#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
from OpenGL.GL import *
import OpenGL.extensions
from aRibeiro.opengl.GLTexture import *
from aRibeiro.opengl.GLRenderBuffer import *
from aRibeiro.window import *

FBO_COLOR_ATTACHMENT_ARRAY = [
    GL_COLOR_ATTACHMENT0,
    GL_COLOR_ATTACHMENT1,
    GL_COLOR_ATTACHMENT2,
    GL_COLOR_ATTACHMENT3,
    GL_COLOR_ATTACHMENT4,
    GL_COLOR_ATTACHMENT5,
    GL_COLOR_ATTACHMENT6,
    GL_COLOR_ATTACHMENT7,
    GL_COLOR_ATTACHMENT8,
    GL_COLOR_ATTACHMENT9,
    GL_COLOR_ATTACHMENT10,
    GL_COLOR_ATTACHMENT11,
    GL_COLOR_ATTACHMENT12,
    GL_COLOR_ATTACHMENT13,
    GL_COLOR_ATTACHMENT14,
    GL_COLOR_ATTACHMENT15
]

class GLDynamicFBO():
    pass

class GLDynamicFBO:
    def __init__(self, window:Window):
        #self.mFBO = GLuint()
        self.window = window
        self.mFBO = glGenFramebuffers(1)
        self.textures = [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]
        self.depthRenderBuffer = None
        self.depthTexture = None
        self.width = 0
        self.height = 0
    def __del__(self):
        self.dispose()
    def dispose(self):
        if self.mFBO == None:
            return
        if self.window.active():
            if glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING) == self.mFBO:
                glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
            if glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING) == self.mFBO:
                glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
            glDeleteFramebuffers(1, [self.mFBO])
        self.mFBO = None
    def setColorAttachment(self, texture:GLTexture, index = 0):
        if texture == None:
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + index, GL_TEXTURE_2D, None, 0)
        else:
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + index, GL_TEXTURE_2D, texture.mTexture, 0)
            self.width = texture.width
            self.height = texture.height
        self.textures[index] = texture
    def setDepthRenderBufferAttachment(self, renderBuffer:GLRenderBuffer):
        if renderBuffer == None:
            if self.depth != None and self.depth.is_depth_stencil:
                glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, None)
            else:
                glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, None)
        else:
            if renderBuffer.is_depth_stencil:
                glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, renderBuffer.mRenderbuffer)
            else:
                glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, renderBuffer.mRenderbuffer)
            self.width = renderBuffer.width
            self.height = renderBuffer.height
        self.depthRenderBuffer = renderBuffer
    def setDepthTextureAttachment(self, texture:GLTexture):
        if texture == None:
            if self.depthTexture != None and self.depthTexture.is_depth_stencil:
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, None, 0)
            else:
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, None, 0)
        else:
            if texture.is_depth_stencil:
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_TEXTURE_2D, texture.mTexture, 0)
            else:
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, texture.mTexture, 0)
            self.width = texture.width
            self.height = texture.height
        self.depthTexture = texture
    def setColorDrawBufferCount(self, count = 1):
        if OpenGL.extensions.hasExtension( 'GL_ARB_draw_buffers' ):
            glDrawBuffers(count, FBO_COLOR_ATTACHMENT_ARRAY)
    def checkCompletness(self):
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status == GL_FRAMEBUFFER_COMPLETE:
            return
        elif status == GL_FRAMEBUFFER_UNSUPPORTED:
            raise Exception("Unsupported framebuffer format")
        elif status == GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
            raise Exception("Framebuffer incomplete, missing attachment")
        #elif status == GL_FRAMEBUFFER_INCOMPLETE_DUPLICATE_ATTACHMENT:
        elif status == 0x8CD8:
            raise Exception("Framebuffer incomplete, duplicate attachment")
        #elif status == GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS:
        elif status == 0x8CD9:
            raise Exception("Framebuffer incomplete, attached images must have same dimensions")
        #elif status == GL_FRAMEBUFFER_INCOMPLETE_FORMATS:
        elif status == 0x8CDA:
            raise Exception("Framebuffer incomplete, attached images must have same format")
        elif status == GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER:
            raise Exception("Framebuffer incomplete, missing draw buffer")
        elif status == GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER:
            raise Exception("Framebuffer incomplete, missing read buffer")
        else:
            raise Exception("Framebuffer not identified error")
    def enable(self):
        # set the current framebuffer to read and draw in one command
        glBindFramebuffer(GL_FRAMEBUFFER, self.mFBO)
    def disable(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    def readPixels(self, width, height, outputRGB, format=GL_RGB, primitive=GL_UNSIGNED_BYTE, attachmentIndex = 0):
        glReadBuffer(GL_COLOR_ATTACHMENT0 + attachmentIndex)
        glReadPixels(0, 0, width, height, format, primitive, outputRGB)
    def blitFrom(self, sourceFBO:GLDynamicFBO, sourceColorIndex, targetColorIndex, bufferToBlitBits = GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT, filter = GL_NEAREST):
        """Copy one FBO to another FBO, It cannot be called when a FBO is active.

        Parameters
        ----------
            sourceFBO: GLDynamicFBO
                The source FBO
            sourceColorIndex: int
                the color attachment index to copy from
            targetColorIndex: int
                the color attachment index to copy to
            bufferToBlitBits:int
                The buffer to copy: GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT or GL_STENCIL_BUFFER_BIT
            filter: int
                GL_NEAREST, GL_LINEAR
       
        Returns
        ----------
            None
        """
        if not OpenGL.extensions.hasExtension( 'GL_EXT_framebuffer_blit' ):
            raise Exception("GL_EXT_framebuffer_blit not found")
        last_read_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)
        last_draw_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)

        glBindFramebuffer(GL_READ_FRAMEBUFFER, sourceFBO.mFBO)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.mFBO)
        glReadBuffer(GL_COLOR_ATTACHMENT0 + sourceColorIndex)
        glDrawBuffer(GL_COLOR_ATTACHMENT0 + targetColorIndex)
        glBlitFramebuffer(0, 0, sourceFBO.width, sourceFBO.height, 0, 0, self.width, self.height, bufferToBlitBits, filter)

        glBindFramebuffer(GL_READ_FRAMEBUFFER, last_read_framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, last_draw_framebuffer)

    def blitFromBackBuffer(self, targetColorIndex, bufferToBlitBits = GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT, filter = GL_NEAREST):
        if not OpenGL.extensions.hasExtension( 'GL_EXT_framebuffer_blit' ):
            raise Exception("GL_EXT_framebuffer_blit not found")
        last_read_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)
        last_draw_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)

        viewport = glGetIntegerv( GL_VIEWPORT )
        glBindFramebuffer(GL_READ_FRAMEBUFFER, 0)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.mFBO)
        glReadBuffer(GL_BACK)
        glDrawBuffer(GL_COLOR_ATTACHMENT0 + targetColorIndex)
        glBlitFramebuffer(viewport[0], viewport[1], viewport[2], viewport[3], 0, 0, self.width, self.height, bufferToBlitBits, filter)

        glBindFramebuffer(GL_READ_FRAMEBUFFER, last_read_framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, last_draw_framebuffer)
    
    def blitToBackBuffer(self, sourceColorIndex, bufferToBlitBits = GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT, filter = GL_NEAREST):
        if not OpenGL.extensions.hasExtension( 'GL_EXT_framebuffer_blit' ):
            raise Exception("GL_EXT_framebuffer_blit not found")
        last_read_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)
        last_draw_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)

        viewport = glGetIntegerv( GL_VIEWPORT )
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.mFBO)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glReadBuffer(GL_COLOR_ATTACHMENT0 + sourceColorIndex)
        glDrawBuffer(GL_BACK)
        glBlitFramebuffer(0, 0, self.width, self.height, viewport[0], viewport[1], viewport[2], viewport[3], bufferToBlitBits, filter)

        glBindFramebuffer(GL_READ_FRAMEBUFFER, last_read_framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, last_draw_framebuffer)

