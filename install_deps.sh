#!/bin/sh
sudo apt-get install -y python3-pip
sudo apt-get install -y libglfw3-dev libglfw3
pip3 install numpy 
pip3 install PyOpenGL PyOpenGL_accelerate
pip3 install glfw
pip3 install Pillow


#wheel
pip install wheel
python -m pip install --upgrade pip
pip install check-wheel-contents