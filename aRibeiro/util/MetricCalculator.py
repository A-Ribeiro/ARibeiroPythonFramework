#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
from OpenGL.GL import *
import numpy as np
from aRibeiro.opengl.GLShader import GLShader
from aRibeiro.opengl.GLDynamicFBO import GLDynamicFBO
from aRibeiro.opengl.GLTexture import GLTexture
#from aRibeiro.util import *
from aRibeiro.window import *


encode_decode_shader_base = math.pow(2,16)#10000.0
encode_decode_shader_use_encoding = True

class MetricValueShader(GLShader):
    def __init__(self, window:Window):
        super().__init__(window)
        vertex_shader = """
            # version 120
            attribute vec4 aPosition;
            attribute vec2 aUV;
            varying vec2 uv;
            void main() {
                uv = aUV;
                gl_Position = aPosition;
            }
        """
            
        fragment_shader = """
            # version 120
            varying vec2 uv;
            uniform sampler2D uTexture;
            uniform vec2 uInputSize;
            uniform vec3 uValueToFilter;
            uniform float uValueThreshould;

            """ + \
                ("""
            vec3 encodeRGB(float f) {
                vec3 enc = vec3(1.0, """+str(encode_decode_shader_base)+""", """+str(encode_decode_shader_base)+"""*"""+str(encode_decode_shader_base)+""") * f;
                enc = fract(enc);
                enc -= enc.yzz * vec3(1. / """+str(encode_decode_shader_base)+""", 1. / """+str(encode_decode_shader_base)+""", 0.);
                return enc;
            }""" if encode_decode_shader_use_encoding else "") \
            + """
            void main() {
                float input_px_percent = 1.0 / ( uInputSize.x * uInputSize.y );
                vec3 value = texture2D(uTexture,uv).rgb;
                value = step( abs(value - uValueToFilter), vec3(uValueThreshould) );
                float selection = value.r * value.g * value.b;
                float result = input_px_percent * selection;
                """ + \
                ("gl_FragColor = vec4(encodeRGB(result),1.0);" if encode_decode_shader_use_encoding else "gl_FragColor = vec4(result,result,result,1.0);") \
                + """
            }
        """

        self.compile(vertex_shader, fragment_shader)
        self.bindAttribLocation(0, "aPosition")
        self.bindAttribLocation(1, "aUV")
        self.link()
        self.uTexture = self.getUniformLocation("uTexture")
        self.uInputSize = self.getUniformLocation("uInputSize")
        self.uValueToFilter = self.getUniformLocation("uValueToFilter")
        self.uValueThreshould = self.getUniformLocation("uValueThreshould")
    
    def setTexture_SamplerUnit(self, texUnit):
        glUniform1i(self.uTexture, texUnit)
    
    def setInput_size(self, width_height:np.array):
        glUniform2fv(self.uInputSize, 1, width_height)
    
    def setValueToFilter(self, filter:np.array):
        glUniform3fv(self.uValueToFilter, 1, filter)

    def setValueThreshould(self, threshould):
        glUniform1f(self.uValueThreshould, threshould)

class ReductionShaderSum(GLShader):
    def __init__(self, window:Window, factor):
        super().__init__(window)
        vertex_shader = """
            # version 120
            attribute vec4 aPosition;
            attribute vec2 aUV;
            varying vec2 uv;
            void main() {
                uv = aUV;
                gl_Position = aPosition;
            }
        """
        fragment_shader = """
            # version 120
            varying vec2 uv;
            uniform sampler2D uTexture;
            uniform vec2 uInputSize;

            void main() {

                vec2 xy = floor( gl_FragCoord.xy );
                
                vec2 input_px_size = vec2( 1.0 ) / uInputSize;
                vec2 half_input_px_size = vec2( 0.5 ) / uInputSize;

                vec2 start = xy * input_px_size * vec2(""" + str(factor) + """)  + half_input_px_size;

                vec3 acc = vec3( 0 );
                for(int x=0;x<""" + str(factor) + """;x++) {
                    for(int y=0;y<""" + str(factor) + """;y++) {
                        vec2 access = start + vec2(x,y) * input_px_size;
                        
                        vec2 outside_access_vec2 = step( access, vec2( 1.0 ) );
                        float outside_access = min( outside_access_vec2.x, outside_access_vec2.y );

                        vec3 value = texture2D( uTexture, access ).rgb;

                        value = value * vec3( outside_access );
                        acc += value;
                    }
                }

                """+ \
                ("""vec3 aux = acc - fract(acc);
                acc = fract(acc) + aux.yzz * vec3(1.0/"""+str(encode_decode_shader_base)+""",1.0/"""+str(encode_decode_shader_base)+""",0.0);
                """ if encode_decode_shader_use_encoding else "") + \
                """
                acc = min(acc, vec3(1));

                gl_FragColor = vec4(acc,1.0);
            }
        """
        self.compile(vertex_shader, fragment_shader)
        self.bindAttribLocation(0, "aPosition")
        self.bindAttribLocation(1, "aUV")
        self.link()
        self.uTexture = self.getUniformLocation("uTexture")
        self.uInputSize = self.getUniformLocation("uInputSize")
    
    def setTexture_SamplerUnit(self, texUnit):
        glUniform1i(self.uTexture, texUnit)
    
    def setInput_size(self, width_height:np.array):
        glUniform2fv(self.uInputSize, 1, width_height)


class FloatFBOReductor:
    def __init__(self, window:Window, source_fbo:GLDynamicFBO, reduction_factor = 3):
        if reduction_factor < 1:
            reduction_factor = 1

        print("[FloatFBOReductor] reduction iterator set to:",1<<reduction_factor)
        
        
        self.vertex = np.array([-1,-1, 0, 
                                 1,-1, 0, 
                                 1, 1, 0, 
                                -1, 1, 0],dtype=np.float32)

        self.uv = np.array([0, 0, 
                            1, 0, 
                            1, 1, 
                            0, 1],dtype=np.float32)

        self.index = np.array([0, 1, 2, 0, 2, 3],dtype=int)

        self.window = window
        self.source_fbo = source_fbo
        self.matric_fbo = GLDynamicFBO(self.window)
        self.matric_fbo.enable()
        self.matric_fbo.setColorAttachment(GLTexture(self.window, source_fbo.width, source_fbo.height, GL_RGB32F), 0)
        self.matric_fbo.checkCompletness()
        self.matric_fbo.disable()
        self.matric_fbo.textures[0].active(0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.matric_fbo.textures[0].deactive(0)
        #print("Creating metric fbo:", self.matric_fbo.width, self.matric_fbo.height)

        self.fbo_array = []
        self.fbo_1x1 = None

        width = source_fbo.width
        height = source_fbo.height

        reduction_factor_valid_bits = (1 << reduction_factor) - 1

        while width != 1 or height != 1:

            if width > 1:
                width_factor_mod_bits = width & reduction_factor_valid_bits
                width = width >> reduction_factor
                #check if need more one element to cover the upper resolution
                if width_factor_mod_bits != 0:
                    width += 1

            if height > 1:
                height_factor_mod_bits = height & reduction_factor_valid_bits
                height = height >> reduction_factor
                #check if need more one element to cover the upper resolution
                if height_factor_mod_bits != 0:
                    height += 1
            
            fbo = GLDynamicFBO(self.window)
            fbo.enable()
            fbo.setColorAttachment(GLTexture(self.window, width, height, GL_RGB32F), 0)
            fbo.checkCompletness()
            fbo.disable()
            fbo.textures[0].active(0)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            fbo.textures[0].deactive(0)
            #print("Creating fbo:", fbo.width, fbo.height)
            self.fbo_array.append(fbo)
        
        self.fbo_1x1 = self.fbo_array[len(self.fbo_array)-1]

        print("[FloatFBOReductor] steps to reduce:",len(self.fbo_array)+1)

        self.reduction_shader = ReductionShaderSum(self.window, 1 << reduction_factor)
        self.metric_shader = MetricValueShader(self.window)
    
    def __del__(self):
        self.dispose()

    def readFromGPU(self) -> float:
        if not self.window.active():
            return
        raw_img = np.zeros(3, dtype=np.float32)
        self.fbo_1x1.enable()
        self.fbo_1x1.readPixels(self.fbo_1x1.width, self.fbo_1x1.height, raw_img, GL_RGB, GL_FLOAT)
        self.fbo_1x1.disable()

        if encode_decode_shader_use_encoding:
            result = float(raw_img[0]) +  \
                     float(raw_img[1]) / encode_decode_shader_base + \
                     float(raw_img[2]) / (encode_decode_shader_base * encode_decode_shader_base)
        else:
            result = raw_img[0]

        return np.min( [result, 1.0] )
    
    def computeMetric(self, color:np.array):

        last_read_framebuffer = glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING)
        last_draw_framebuffer = glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING)
        last_program = glGetIntegerv(GL_CURRENT_PROGRAM)
        viewport = glGetIntegerv( GL_VIEWPORT )

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, float_size(3), self.vertex)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, False, float_size(2), self.uv)

        self.metric_shader.enable()
        self.metric_shader.setInput_size(np.array([self.source_fbo.width,self.source_fbo.height],dtype=np.float32))
        self.metric_shader.setValueToFilter(color)
        self.metric_shader.setValueThreshould(0.5/256.0)
        self.metric_shader.setTexture_SamplerUnit(0)
        self.source_fbo.textures[0].active(0)

        self.matric_fbo.enable()
        glViewport(0,0,self.matric_fbo.width,self.matric_fbo.height)

        glDrawElements(GL_TRIANGLES, np.size(self.index), GL_UNSIGNED_INT, self.index)

        src_fbo = self.matric_fbo

        self.reduction_shader.enable()
        self.reduction_shader.setTexture_SamplerUnit(0)

        for fbo in self.fbo_array:
            fbo.enable()
            glViewport(0,0,fbo.width,fbo.height)

            self.reduction_shader.setInput_size( np.array([src_fbo.width,src_fbo.height],dtype=np.float32))
            #self.reduction_shader.setOutput_size( np.array([fbo.width,fbo.height],dtype=np.float32))
            src_fbo.textures[0].active(0)

            glDrawElements(GL_TRIANGLES, np.size(self.index), GL_UNSIGNED_INT, self.index)

            src_fbo = fbo
        
        src_fbo.disable()
        src_fbo.textures[0].deactive(0)

        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(0)
        
        glBindFramebuffer(GL_READ_FRAMEBUFFER, last_read_framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, last_draw_framebuffer)
        glViewport(viewport[0],viewport[1],viewport[2],viewport[3])
        glUseProgram(last_program)



    def dispose(self):
        for fbo in self.fbo_array:
            fbo.textures[0].dispose()
            fbo.dispose()
        self.fbo_array.clear()
        self.fbo_1x1 = None
        self.matric_fbo.textures[0].dispose()
        self.matric_fbo.dispose()
        


class MetricCalculator:
    def __init__(self, window:Window, fbo:GLDynamicFBO):
        self.fbo_reductor = FloatFBOReductor(window, fbo)
    def __del__(self):
        self.dispose()
    def dispose(self):
        if self.fbo_reductor != None:
            self.fbo_reductor.dispose()
        self.fbo_reductor = None
    def computeColorPercentage(self, color)->float:
        self.fbo_reductor.computeMetric(color)
        result = self.fbo_reductor.readFromGPU()
        return result
    
