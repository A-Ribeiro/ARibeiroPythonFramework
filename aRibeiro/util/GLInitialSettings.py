from OpenGL.GL import *

def GLInitialSettings():
    #disable depth test... because we are drawing 2D things
    glDisable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)
    #enable triangle back face culling
    glFrontFace(GL_CCW)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    #enabling transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBlendEquation(GL_FUNC_ADD)
    glDisable(GL_ALPHA_TEST)
    #drawing beatiful lines
    glDisable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    #disabling wireframe
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    #enabling write on all colors
    glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)