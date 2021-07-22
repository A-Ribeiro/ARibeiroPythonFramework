#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
import numpy as np
from aRibeiro.math import *
from aRibeiro.opengl import *
#from multiprocessing import RLock
from threading import Semaphore, get_ident
# threading.get_ident() works, or threading.current_thread().ident (or threading.currentThread().ident for Python < 2.6).
from aRibeiro.util.LineRenderer import *
from aRibeiro.window import *
#from aRibeiro.tools.MetricCalculator import *
from aRibeiro.util.MetricCalculator import MetricCalculator

import time

###########################################
#
#
# User class...
#
#
###########################################

class GLVirtualImageCommand:
    def __init__(self, op, arg):
        self.op = op
        self.processed = False
        self.responded = False
        self.response = None
        self.arg = arg


class GLVirtualImage:
    def __init__(self, window:Window, width, height, line_width):
        self.window = window
        self.width = width
        self.height = height
        self.projection = projection_ortho_rh_negative_one(0, self.width, 0, self.height, -1000, 1000)
        self.texture = GLTexture(self.window, width, height)
        #self.depth_buffer = GLRenderBuffer(self.window, width, height)
        self.fbo = GLDynamicFBO(self.window)
        self.fbo.enable()
        self.fbo.setColorAttachment(self.texture, 0)
        #self.fbo.setDepthRenderBufferAttachment(self.depth_buffer)
        self.fbo.setColorDrawBufferCount(1)
        self.fbo.checkCompletness()
        self.fbo.disable()
        self.lineRenderer = LineRenderer(self.window, line_width)
        self.raw_img = np.zeros(self.width*self.height*3, dtype=np.uint8)
        #reshape hold the original buffer pointer
        self.img = np.reshape( self.raw_img, [self.height, self.width, 3] )
        self.active = False

        self.metric_calculator = MetricCalculator(self.window, self.fbo)

        self.post_semaphore = Semaphore()
        self.response_semaphore = Semaphore()
        self.response_semaphore.acquire()
        self.command = None

        self.opengl_thread_ident = get_ident()
        self.thread_end = False
    def __del__(self):
        self.dispose()
    def dispose(self):
        if self.opengl_thread_ident != get_ident():
            raise Exception("Trying to execute OpenGL commands outside main Thread...")

        self.post_semaphore.acquire(blocking=True)
        self.thread_end = True
        self.post_semaphore.release()

        #commands processing
        if not self.window.active():
            return
        #glUseProgram(0)
        self.__updateThreadCommands()

        self.metric_calculator.dispose()
        self.lineRenderer.dispose()
        self.fbo.dispose()
        #self.depth_buffer.dispose()
        self.texture.dispose()
    def beginDraw(self):
        if self.opengl_thread_ident != get_ident():
            raise Exception("Trying to execute OpenGL commands outside main Thread...")
        self.fbo.enable()
        glViewport(0, 0, self.width, self.height)
        self.active = True
        self.__updateThreadCommands_pre()
    def endDraw(self):
        if self.opengl_thread_ident != get_ident():
            raise Exception("Trying to execute OpenGL commands outside main Thread...")
        self.__updateThreadCommands_post()
        self.fbo.disable()
        self.active = False
    def clear(self, background_color = [0,0,0,1]):
        if self.opengl_thread_ident != get_ident():
            # executing from another thread
            self.__syncClear(background_color)
            return
        if self.active:
            glClearColor(background_color[0], background_color[1], background_color[2], background_color[3])
            glClear(GL_COLOR_BUFFER_BIT)
        else:
            if not self.window.active():
                return
            self.beginDraw()
            glClearColor(background_color[0], background_color[1], background_color[2], background_color[3])
            glClear(GL_COLOR_BUFFER_BIT)
            self.endDraw()
    def readImageRGB(self, copyValue=False):
        if self.opengl_thread_ident != get_ident():
            # executing from another thread
            return self.__syncReadImageRGB(copyValue)
        if self.active:
            self.fbo.readPixels(self.width,self.height,self.raw_img, GL_RGB, GL_UNSIGNED_BYTE)
        else:
            if self.window.active():
                self.fbo.enable()
                self.fbo.readPixels(self.width,self.height,self.raw_img, GL_RGB, GL_UNSIGNED_BYTE)
                self.fbo.disable()
        if copyValue:
            return np.copy(self.img)
        else:
            return self.img
    def computeColorPercentage(self, color) -> float :
        if self.opengl_thread_ident != get_ident():
            # executing from another thread
            return self.__syncComputeWhitePercentage(color)
        result = np.float32(0.0)
        if self.active:
            result = self.metric_calculator.computeColorPercentage(color)
        else:
            if self.window.active():
                result = self.metric_calculator.computeColorPercentage(color)
        return result
    #
    # Multithreading commands
    #
    def __updateThreadCommands(self):
        self.__updateThreadCommands_pre()
        self.__updateThreadCommands_post()
    def __updateThreadCommands_pre(self):
        if self.post_semaphore.acquire(blocking=False):
            if (self.command != None) and (not self.command.processed):
                if self.command.op == "clear":
                    self.clear(self.command.arg)
                    self.command.processed = True
            self.post_semaphore.release()
    def __updateThreadCommands_post(self):
        if self.post_semaphore.acquire(blocking=False):
            response = None
            if (self.command != None) and (not self.command.processed):
                if self.command.op == "readImageRGB":
                    response = self.readImageRGB(self.command.arg)
                    self.command.processed = True
                elif self.command.op == "computeWhitePercentage":
                    response = self.computeColorPercentage(self.command.arg)
                    self.command.processed = True

            self.post_semaphore.release()
            # if the command is processed, 
            # so we can return the value to the original caller
            if (self.command != None) and (self.command.processed) and (not self.command.responded):
                self.command.response = response
                self.command.responded = True
                self.response_semaphore.release()
    def __syncClear(self, background_color):
        if not self.__setCommand(GLVirtualImageCommand(op="clear", arg=background_color)):
            return
        # sync waiting response from main thread
        self.response_semaphore.acquire(blocking=True)
        self.__resetCommand()
    def __syncReadImageRGB(self, copyValue):
        if not self.__setCommand(GLVirtualImageCommand(op="readImageRGB", arg=copyValue)):
            return self.img #returns the last queried image...
        # sync waiting response from main thread
        self.response_semaphore.acquire(blocking=True)
        response = self.command.response
        self.__resetCommand()
        return response
    def __syncComputeWhitePercentage(self, color):
        if not self.__setCommand(GLVirtualImageCommand(op="computeWhitePercentage", arg=color)):
            return 0.0 #returns the last queried image...
        # sync waiting response from main thread
        self.response_semaphore.acquire(blocking=True)
        response = self.command.response
        self.__resetCommand()
        return response
    def __setCommand(self, command):
        # BEGIN CRITICAL AREA set self.command
        self.post_semaphore.acquire()
        if self.thread_end:
            self.post_semaphore.release()
            return False
        while self.command != None:
            self.post_semaphore.release()
            time.sleep(0.002) #2ms
            self.post_semaphore.acquire()
        if self.thread_end:
            self.post_semaphore.release()
            return False
        # name, processed, parameters
        self.command = command
        self.post_semaphore.release()
        # END CRITICAL AREA set self.command
        return True
    def __resetCommand(self):
        # critical area self.command
        self.post_semaphore.acquire()
        self.command = None
        self.post_semaphore.release()

