#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
import glfw
from aRibeiro.math import *
from OpenGL.GL import *
import OpenGL.extensions


###########################################
#
#
# Window related stuff...
#
#
###########################################
def FullScreenWindow():
    return Window(None,None,True)

class Window:
    def __init__(self, width, height, fullscreen = False):
        self.fence = None
        self.resize_callback = None
        self.width = width
        self.width = height

        def default_key_callback(win, key, scancode, action, mods):
            if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
                self.close()
        def default_window_resize_callback(win, width, height):
            self.width = width
            self.height = height
            sizeX_2 = self.width/self.height
            sizeY_2 = self.height/self.width
            if sizeX_2 > sizeY_2:
                sizeY_2 = 1
            else:
                sizeX_2 = 1
            self.sizeX_2 = sizeX_2
            self.sizeY_2 = sizeY_2
            #print("windowImageSize_2: ",self.sizeX_2,self.sizeY_2)
            self._2d_projection_matrix = projection_ortho_rh_negative_one(-self.sizeX_2, self.sizeX_2, -self.sizeY_2, self.sizeY_2, -1000, 1000)
            if self.resize_callback != None:
                self.resize_callback(self)

        glfw.init()
        glfw.window_hint(glfw.DEPTH_BITS, 0)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        #glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        #glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, GL_TRUE)
        glfw.window_hint(glfw.SAMPLES, 0)

        #glfw.window_hint(glfw.VISIBLE, False)

        

        if fullscreen:
            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            glfw.window_hint(glfw.RED_BITS, mode.bits.red)
            glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
            glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
            glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

            self.window = glfw.create_window(mode.size.width, mode.size.height, 'GLFW Window',  monitor, None)
            self.width = mode.size.width
            self.height = mode.size.height
        else:
            self.window = glfw.create_window(width, height, 'GLFW Window',  None, None)
            self.width = width
            self.height = height
        
        glfw.set_key_callback(self.window, default_key_callback)
        glfw.set_window_size_callback(self.window, default_window_resize_callback)

        self._2d_projection_matrix = IdentityMatrix()
        self.sizeX_2 = 1
        self.sizeY_2 = 1
        default_window_resize_callback(self.window, self.width, self.height)

        self.active()


        self._has_GL_ARB_sync = OpenGL.extensions.hasExtension( 'GL_ARB_sync' )
        

        #vsync on
        glfw.swap_interval(1)

        renderer = glGetString(GL_RENDERER).decode()
        print('Renderer:',  renderer)
        version = glGetString(GL_VERSION).decode()
        print('OpenGL version supported: ', version)
        ext_count = glGetIntegerv(GL_NUM_EXTENSIONS)
        ext_str = ""
        for i in range(ext_count):
            if len(ext_str) == 0:
                ext_str = glGetStringi(GL_EXTENSIONS,i).decode()
            else:
                ext_str += ", " + glGetStringi(GL_EXTENSIONS,i).decode()
        print("Extensions:",ext_str)

        glFlush()


    def __del__(self):
        self.dispose()
    
    def active(self):
        if self.window == None:
            return False
        glfw.make_context_current(self.window)
        return True

    def close(self):
        glfw.set_window_should_close(self.window, True)
    
    def should_close(self):
        return glfw.window_should_close(self.window)
    
    def can_swap_buffer(self):
        if self._has_GL_ARB_sync and self.fence != None:
            aux = glClientWaitSync(self.fence, GL_SYNC_FLUSH_COMMANDS_BIT, 0)
            #aux = glClientWaitSync(self.fence, 0, 0)
            #return  != GL_TIMEOUT_EXPIRED
            return aux == GL_ALREADY_SIGNALED or aux == GL_CONDITION_SATISFIED
        return True

    def swap_buffers(self):
        if self._has_GL_ARB_sync and self.fence != None:
            glDeleteSync(self.fence)
            self.fence = None
        glfw.swap_buffers(self.window)
        if self._has_GL_ARB_sync:
            self.fence = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
        

    
    def process_events(self):
        glfw.poll_events()
    
    def dispose(self):
        if self.window == None:
            return
        glfw.destroy_window(self.window)
        self.window = None