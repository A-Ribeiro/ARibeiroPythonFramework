#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
from time import sleep
from OpenGL.GL import *
import numpy as np
from aRibeiro.util.GLVirtualImage import GLVirtualImage
from aRibeiro.util.GLInitialSettings import GLInitialSettings
from aRibeiro.opengl.GLShader import TextureShader
from aRibeiro.window import *

class SensorVis:
    def __init__(self, window_width, window_height, map_width, map_height, line_width = 1.0):
        self.window_width = window_width
        self.window_height = window_height 

        self.map_width = map_width
        self.map_height = map_height 

        self.line_width = line_width

        # create gl window
        self.window = Window(self.window_width, self.window_height)
        self.window.resize_callback = self.OnWindowResize

        # initialize opengl
        GLInitialSettings()

        # initialize virtual framebuffer image
        self.virtual_image = GLVirtualImage(self.window, self.map_width, self.map_height, self.line_width)
        self.virtual_image.clear([0,0,0,1])

        # shader used to draw the quad in the simulation
        self.texture_shader = TextureShader(self.window)
        self.model_matrix = IdentityMatrix()

        # vertex to be drawn
        self.vertex = np.array([-1,-1, 0, 
                                 1,-1, 0, 
                                 1, 1, 0, 
                                -1, 1, 0],dtype=np.float32)

        self.uv = np.array([0, 0, 
                            1, 0, 
                            1, 1, 
                            0, 1],dtype=np.float32)

        self.index = np.array([0, 1, 2, 0, 2, 3],dtype=int)

        # do the first resize to avoid drawing nothing
        self.OnWindowResize(self.window)

    def OnWindowResize(self, windowInstance):
        aspectWindow = self.window.width / self.window.height
        aspectVirtualImage = self.virtual_image.width / self.virtual_image.height

        if aspectWindow > aspectVirtualImage:
            # fit_height
            self.model_matrix = ScaleMatrix([self.virtual_image.width / self.virtual_image.height,1,1])
            if self.window.width < self.window.height:
                factor = self.window.height / self.window.width
                self.model_matrix = self.model_matrix @ ScaleMatrix([factor,factor,1])
        else:
            # fit_width
            self.model_matrix = ScaleMatrix([1, self.virtual_image.height / self.virtual_image.width,1])
            if self.window.height < self.window.width:
                factor = self.window.width / self.window.height
                self.model_matrix = self.model_matrix @ ScaleMatrix([factor,factor,1])

    def windowClosed(self):
        return self.window.should_close()

    def update(self):
        self.window.active()

        while (self.virtual_image.command != None) or (np.size(self.virtual_image.lineRenderer.vertex_line_pos) > 0):
            # more secure process all lines in one big critical section...
            self.virtual_image.lineRenderer.lock.acquire() 
            #if np.size(self.virtual_image.lineRenderer.vertex_line_pos) > 0 or self.virtual_image.command != None:
            self.virtual_image.beginDraw()
            self.virtual_image.lineRenderer.draw(self.virtual_image.projection)
            self.virtual_image.endDraw()
            self.virtual_image.lineRenderer.lock.release()

        
        if self.window.can_swap_buffer():
            # draw code
            glViewport(0, 0, self.window.width, self.window.height)
            glClearColor(0,0,0,1)
            glClear(GL_COLOR_BUFFER_BIT)
            
            self.texture_shader.enable()
            self.texture_shader.setMVP_Matrix4x4( self.window._2d_projection_matrix @ self.model_matrix )
            self.texture_shader.setTexture_SamplerUnit(0)
            self.virtual_image.texture.active(0)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, False, float_size(3), self.vertex)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, False, float_size(2), self.uv)

            glDrawElements(GL_TRIANGLES, np.size(self.index), GL_UNSIGNED_INT, self.index)

            glDisableVertexAttribArray(1)
            glDisableVertexAttribArray(0)

            self.virtual_image.texture.deactive(0)

            # swap buffers
            self.window.swap_buffers()

        self.window.process_events()
        
    def finish(self):
        # save map image
        img = self.virtual_image.readImageRGB()
        from PIL import Image, ImageOps
        im = ImageOps.flip( Image.fromarray(img) )
        im.save("output_map.png", format='png')

        # dispose resources
        self.texture_shader.dispose()
        self.virtual_image.dispose()
        self.window.dispose()