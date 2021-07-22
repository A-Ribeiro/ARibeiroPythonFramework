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
import numpy as np
from aRibeiro.window import *

class GLTexture:
    def __init__(self, window:Window, width, height, format = GL_RGB):
        self.window = window
        self.width = width
        self.height = height
        self.is_depth_stencil = False
        self.internal_format = 0
        self.input_format = GL_RGB
        self.input_data_type = GL_UNSIGNED_BYTE
        self.input_alignment = 4
        self.input_raw_element_size = 1
        self.input_component_count = 1
        #self.mTexture = GLuint()
        self.mTexture = glGenTextures(1)
        self.active(0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self.setSize(width, height, format)
        self.deactive(0)
    def __del__(self):
        self.dispose()
    def dispose(self):
        if self.mTexture == None:
            return
        if self.window.active():
            glDeleteTextures([self.mTexture])
        self.mTexture = None
    def active(self, texUnit):
        glActiveTexture(GL_TEXTURE0 + texUnit)
        glBindTexture(GL_TEXTURE_2D, self.mTexture)
    def deactive(self, texUnit):
        glActiveTexture(GL_TEXTURE0 + texUnit)
        glBindTexture(GL_TEXTURE_2D, 0)
    def setSize(self, width, height, format = GL_RGB):
        self.is_depth_stencil = False
        self.internal_format = format
        if self.internal_format == GL_RGB:
            self.input_format = GL_RGB
            self.input_data_type = GL_UNSIGNED_BYTE
            self.input_alignment = 1
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 3
            self.input_component_count = 3
        elif self.internal_format == GL_DEPTH_COMPONENT16 or self.internal_format == GL_DEPTH_COMPONENT24 or self.internal_format == GL_DEPTH_COMPONENT32:
            self.input_format = GL_DEPTH_COMPONENT
            self.input_data_type = GL_FLOAT
            self.input_alignment = 4
            self.input_raw_element_size = sizeof(ctypes.c_float) * 1
            self.input_component_count = 1
            # depth buffer force to nearest filtering...
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        elif self.internal_format == GL_STENCIL_INDEX8:
            self.input_format = GL_STENCIL_INDEX
            self.input_data_type = GL_UNSIGNED_BYTE
            self.input_alignment = 1
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 1
            self.input_component_count = 1
            # index buffer force to nearest filtering...
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        elif self.internal_format == GL_DEPTH24_STENCIL8:
            self.input_format = GL_DEPTH_STENCIL
            self.input_data_type = GL_UNSIGNED_INT_24_8
            self.input_alignment = 4
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 4
            self.input_component_count = 1
            # depth buffer force to nearest filtering...
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            self.is_depth_stencil = True
        elif self.internal_format == GL_RGBA16F or self.internal_format == GL_RGBA32F:
            self.input_format = GL_RGBA
            self.input_data_type = GL_FLOAT
            self.input_alignment = 4
            self.input_raw_element_size = sizeof(ctypes.c_float) * 4
            self.input_component_count = 4
        elif self.internal_format == GL_RGB16F or self.internal_format == GL_RGB32F:
            self.input_format = GL_RGB
            self.input_data_type = GL_FLOAT
            self.input_alignment = 4
            self.input_raw_element_size = sizeof(ctypes.c_float) * 3
            self.input_component_count = 3
        elif self.internal_format == GL_R16F or self.internal_format == GL_R32F:
            self.input_format = GL_R
            self.input_data_type = GL_FLOAT
            self.input_alignment = 4
            self.input_raw_element_size = sizeof(ctypes.c_float) * 1
            self.input_component_count = 1
        elif self.internal_format == GL_SRGB:
            self.input_format = GL_RGB
            self.input_data_type = GL_UNSIGNED_BYTE
            self.input_alignment = 1
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 3
            self.input_component_count = 3
        elif self.internal_format == GL_SRGB_ALPHA:
            self.input_format = GL_RGBA
            self.input_data_type = GL_UNSIGNED_BYTE
            self.input_alignment = 4
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 4
            self.input_component_count = 4
        elif self.internal_format == GL_R:
            self.input_format = GL_R
            self.input_data_type = GL_UNSIGNED_BYTE
            self.input_alignment = 1
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 1
            self.input_component_count = 1
        elif self.internal_format == GL_ALPHA:
            self.input_format = GL_ALPHA
            self.input_data_type = GL_UNSIGNED_BYTE
            self.input_alignment = 1
            self.input_raw_element_size = sizeof(ctypes.c_uint8) * 1
            self.input_component_count = 1
        else:
            raise Exception('Texture wrong format...')
        
        if self.input_data_type == GL_FLOAT and not OpenGL.extensions.hasExtension( 'GL_ARB_texture_float' ):
            raise Exception("GL_ARB_texture_float not found")

        glTexImage2D(GL_TEXTURE_2D, 0, self.internal_format, width, height, 0, self.input_format, self.input_data_type, None)
    def upload(self, data):
        glPixelStorei(GL_PACK_ALIGNMENT, self.input_alignment)
        #glPixelStorei(GL_UNPACK_ALIGNMENT, self.input_alignment)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, self.input_format, self.input_data_type, data)
        glPixelStorei(GL_PACK_ALIGNMENT, 4)
        #glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    def download(self, output:np.array = None):
        result = output
        if not np.any(output):
            if self.input_data_type == GL_UNSIGNED_BYTE:
                result = np.zeros([self.width, self.height, self.input_component_count], dtype=np.uint8)
            elif self.input_data_type == GL_FLOAT:
                result = np.zeros([self.width, self.height, self.input_component_count], dtype=np.float32)
            elif self.input_data_type == GL_UNSIGNED_INT_24_8:
                result = np.zeros([self.width, self.height, self.input_component_count], dtype=np.uint32)
            else:
                raise Exception("Wrong input_data_type...")

        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.mTexture, 0)

        glPixelStorei(GL_UNPACK_ALIGNMENT, self.input_alignment)
        glReadPixels(0, 0, self.width, self.height, self.input_format, self.input_data_type, result)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 4)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDeleteFramebuffers(1, [fbo])

        return result
    def generateMipMap(self):
        if not OpenGL.extensions.hasExtension( 'GL_SGIS_generate_mipmap' ):
            raise Exception("GL_SGIS_generate_mipmap not found")
        self.active(0)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.deactive(0)
    def setAnisioLevel(self, level):
        if OpenGL.extensions.hasExtension( 'GL_EXT_texture_filter_anisotropic' ):
            self.active(0)
            GL_TEXTURE_MAX_ANISOTROPY_EXT=_C('GL_TEXTURE_MAX_ANISOTROPY_EXT',0x84FE)
            GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT=_C('GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT',0x84FF)
            max_anisio = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
            level = np.clip(level, 1.0, max_anisio)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, level)
            self.deactive(0)
    def setAsShadowMapFiltering(self, enable = True, compare_as = GL_LEQUAL):
        self.active(0)
        if enable:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_REF_TO_TEXTURE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, compare_as)
        else:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)
        self.deactive(0)
