#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
import numpy as np
from OpenGL.GL import *
from aRibeiro.window import *

class GLShader:
    def __init__(self, window:Window):
        self.window = window
        self.program_id = None
        self.v_shader = None
        self.f_shader = None
    
    def __del__(self):
        self.dispose()
    
    def dispose(self):
        if self.program_id == None:
            return
        if self.window.active():
            if glGetIntegerv(GL_CURRENT_PROGRAM) == self.program_id:
                glUseProgram(0)
            glDeleteProgram(self.program_id)
        self.program_id = None
    
    def compile(self, vertex, fragment):

        self.v_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.v_shader, [vertex], None)
        glCompileShader(self.v_shader)
        status = glGetShaderiv(self.v_shader, GL_COMPILE_STATUS)
        if status != 1:
            print('VERTEX SHADER ERROR')
            print(glGetShaderInfoLog(self.v_shader).decode())
            raise Exception("VERTEX SHADER ERROR")
        
        self.f_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.f_shader, [fragment], None)
        glCompileShader(self.f_shader)
        status = glGetShaderiv(self.f_shader, GL_COMPILE_STATUS)
        if status != 1:
            print('FRAGMENT SHADER ERROR')
            print(glGetShaderInfoLog(self.f_shader).decode())
            raise Exception("FRAGMENT SHADER ERROR")

        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, self.v_shader)
        glAttachShader(self.program_id, self.f_shader)

    def bindAttribLocation(self, location, attrib_name):
        glBindAttribLocation(self.program_id, location, attrib_name)

    def link(self):
        glLinkProgram(self.program_id)
        status = glGetProgramiv(self.program_id, GL_LINK_STATUS)
        if status != 1:
            print('status', status)
            print('SHADER PROGRAM', glGetShaderInfoLog(self.program_id).decode())
            raise Exception("SHADER LINK ERROR")

        glDetachShader(self.program_id, self.v_shader)
        glDetachShader(self.program_id, self.f_shader)

        glDeleteShader(self.v_shader)
        glDeleteShader(self.f_shader)

        self.v_shader = None
        self.f_shader = None

    def enable(self):
        glUseProgram(self.program_id)
    
    def disable(self):
        glUseProgram(0)

    def getAttribLocation(self, name):
        return glGetAttribLocation(self.program_id, name)
    
    def getUniformLocation(self, name):
        return glGetUniformLocation(self.program_id, name)
    

class PositionColorShader(GLShader):
    def __init__(self, window:Window):
        super().__init__(window)
        vertex_shader = """
            # version 120
            attribute vec4 aPosition;
            attribute vec4 aColor;
            uniform mat4 uMVP;
            varying vec4 color;
            void main() {
                color = aColor;
                gl_Position = uMVP * aPosition;
            }
        """
        fragment_shader = """
            # version 120
            varying vec4 color;
            void main() {
                gl_FragColor = color;
            }
        """
        self.compile(vertex_shader, fragment_shader)
        self.bindAttribLocation(0, "aPosition")
        self.bindAttribLocation(1, "aColor")
        self.link()
        self.uMVP = self.getUniformLocation("uMVP")
    
    def setMVP_Matrix4x4(self, mvp:np.array):
        #aux = np.reshape(mvp,[16])
        #glUniformMatrix4fv(self.uMVP, 1, GL_TRUE, aux)
        glUniformMatrix4fv(self.uMVP, 1, GL_TRUE, mvp)
        


class TextureShader(GLShader):
    def __init__(self, window:Window):
        super().__init__(window)
        vertex_shader = """
            # version 120
            attribute vec4 aPosition;
            attribute vec2 aUV;
            uniform mat4 uMVP;
            varying vec2 uv;
            void main() {
                uv = aUV;
                gl_Position = uMVP * aPosition;
            }
        """
        fragment_shader = """
            # version 120
            varying vec2 uv;
            uniform sampler2D uTexture;
            void main() {
                gl_FragColor = texture2D(uTexture, uv);
            }
        """
        self.compile(vertex_shader, fragment_shader)
        self.bindAttribLocation(0, "aPosition")
        self.bindAttribLocation(1, "aUV")
        self.link()
        self.uMVP = self.getUniformLocation("uMVP")
        self.uTexture = self.getUniformLocation("uTexture")
    
    def setMVP_Matrix4x4(self, mvp:np.array):
        #aux = np.reshape(mvp,[16])
        #glUniformMatrix4fv(self.uMVP, 1, GL_TRUE, aux)
        glUniformMatrix4fv(self.uMVP, 1, GL_TRUE, mvp)
    def setTexture_SamplerUnit(self, texUnit):
        glUniform1i(self.uTexture, texUnit)

