#
# For this is how God loved the world:<br/>
# he gave his only Son, so that everyone<br/>
# who believes in him may not perish<br/>
# but may have eternal life.
# 
# John 3:16
#
from aRibeiro.tools import SensorVis;
import time
from threading import Thread
from multiprocessing import Value
import random

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

VIRTUAL_IMAGE_WIDTH = 1920
VIRTUAL_IMAGE_HEIGHT = 1080
VIRTUAL_IMAGE_LINE_WIDTH = 1.0

sensorVis = SensorVis(
    WINDOW_WIDTH,WINDOW_HEIGHT,
    VIRTUAL_IMAGE_WIDTH,VIRTUAL_IMAGE_HEIGHT,
    VIRTUAL_IMAGE_LINE_WIDTH
)

terminateFlag = Value("i", 0)
def AnotherThreadLineDrawer(terminateFlag:Value, sensorVis:SensorVis):
    while not terminateFlag.value:
        random_start_sec = 0.03
        random_end_sec = 0.07
        time.sleep( random.random() * (random_end_sec-random_start_sec) + random_start_sec )

        random_v_count = random.randint(10, 200)

        #virtualImage.clear([0,0,1,1])

        for i in range(random_v_count):
            v1 = [random.random()*sensorVis.map_width,random.random()*sensorVis.map_height,0]
            v2 = [random.random()*sensorVis.map_width,random.random()*sensorVis.map_height,0]
            sensorVis.virtual_image.lineRenderer.addLine(
                v1, # vertex A
                v2, # vertex B
                [random.random(),0,1,1.0], #color a
                [random.random(),1,0,1.0] #color b
            )

        # when call this methods from another thread, 
        # it will block the execution until the result from the main thread is done
        imageRGB = sensorVis.virtual_image.readImageRGB(copyValue=False)

thread = Thread( target=AnotherThreadLineDrawer, args=[terminateFlag, sensorVis] )
thread.start()

while not sensorVis.windowClosed():
    sensorVis.update()

terminateFlag.value = 1
# need to call finish to close the window and unlock the drawing thread...
sensorVis.finish()

thread.join()
