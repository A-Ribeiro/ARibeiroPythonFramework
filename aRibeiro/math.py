#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
import math
import numpy as np
from OpenGL.GL import sizeof, ctypes

###########################################
#
#
# Math related stuff...
#
#
###########################################

DEG2RAD = float(0.0174532925199432957692222222222222)
RAD2DEG = float(57.2957795130823208767981548141052)

def IdentityMatrix():
    return np.array([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ],dtype=np.float32)

def TranslateMatrix(vec:np.array):
    return np.array([
        [1,0,0,vec[0]],
        [0,1,0,vec[1]],
        [0,0,1,vec[2]],
        [0,0,0,1]
    ],dtype=np.float32)

def ScaleMatrix(vec:np.array):
    return np.array([
        [vec[0],0,0,0],
        [0,vec[1],0,0],
        [0,0,vec[2],0],
        [0,0,0,1]
    ],dtype=np.float32)

def RotateMatrixX(_phi_deg):
    _phi_ = _phi_deg * DEG2RAD
    c = math.cos(_phi_)
    s = math.sin(_phi_)
    return np.array([
        [1,0,0,0],
        [0,c,-s,0],
        [0,s,c,0],
        [0,0,0,1]
    ],dtype=np.float32)

def RotateMatrixY(_theta_deg):
    _theta_ = _theta_deg * DEG2RAD
    c = math.cos(_theta_)
    s = math.sin(_theta_)
    return np.array([
        [c,0,s,0],
        [0,1,0,0],
        [-s,0,c,0],
        [0,0,0,1]
    ],dtype=np.float32)

def RotateMatrixZ(_psi_deg):
    _psi_ = _psi_deg * DEG2RAD
    c = math.cos(_psi_)
    s = math.sin(_psi_)
    return np.array([
        [c,-s,0,0],
        [s,c,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ],dtype=np.float32)

def EulerRotateMatrix(roll_deg, pitch_deg, yaw_deg):
    return RotateMatrixZ(yaw_deg) @ RotateMatrixY(pitch_deg) @ RotateMatrixX(roll_deg)

def projection_perspective_rh_negative_one(FovY_degree, aspectX, near_, far_):
    if aspectX == 0 or near_-far_ == 0:
        return IdentityMatrix()
    focus = math.tan( FovY_degree * DEG2RAD / 2.0 )
    if focus == 0:
        focus = 0.000002
    focus = 1.0 / focus
    return np.array([
        [focus / aspectX,0    ,0                               ,0                                ],
        [0              ,focus,0                               ,0                                ],
        [0              ,0    ,(near_ + far_) / (near_ - far_) ,(2.0*near_*far_) / (near_ - far_)],
        [0              ,0    ,-1                              ,0                                ]
    ],dtype=np.float32)

def projection_ortho_rh_negative_one(Left, Right, Bottom, Top, Near, Far):
    return np.array([
        [2.0 / (Right - Left),0                   ,0                  ,-(Right + Left) / (Right - Left)],
        [0                   ,2.0 / (Top - Bottom),0                  ,-(Top + Bottom) / (Top - Bottom)],
        [0                   ,0                   ,-2.0 / (Far - Near),-(Far + Near) / (Far - Near)    ],
        [0                   ,0                   ,0                  ,1                               ]
    ],dtype=np.float32)

def float_size(n=1):
    return sizeof(ctypes.c_float) * n

def pointer_offset(n=0):
    return ctypes.c_void_p(float_size(n))