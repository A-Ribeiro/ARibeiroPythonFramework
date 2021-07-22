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

        sensorVis.virtual_image.clear([0,0,0,1])

        for i in range(random_v_count):
            v1 = [random.random()*sensorVis.map_width,random.random()*sensorVis.map_height,0]
            v2 = [random.random()*sensorVis.map_width,random.random()*sensorVis.map_height,0]
            sensorVis.virtual_image.lineRenderer.addLine(
                v1, # vertex A
                v2, # vertex B
                [1,1,1,1], #color a
                [1,1,1,1] #color b
            )
        
        # test query the white percent 
        gpu_start = time.time()
        gpu_value = sensorVis.virtual_image.computeColorPercentage([1,1,1])
        gpu_end = time.time()

        print("GPU -> value:",gpu_value,"time:", gpu_end-gpu_start, "s")



thread = Thread( target=AnotherThreadLineDrawer, args=[terminateFlag, sensorVis] )
thread.start()

while not sensorVis.windowClosed():
    sensorVis.update()
terminateFlag.value = 1
while thread.is_alive():
    sensorVis.update()


print("window closed...")

print("gpu processing...")

gpu_start = time.time()
gpu_value = sensorVis.virtual_image.computeColorPercentage([1,1,1])
gpu_end = time.time()

print("GPU -> value:",gpu_value,"time:", gpu_end-gpu_start, "s")

print("cpu processing...")

cpu_start = time.time()
rgb = sensorVis.virtual_image.readImageRGB()
count = 0
for col in rgb:
    for row in col:
        if row[0] > 200:
            count += 1
cpu_value = count/(VIRTUAL_IMAGE_WIDTH*VIRTUAL_IMAGE_HEIGHT)
cpu_end = time.time()

print("CPU -> value:",cpu_value,"time:", cpu_end-cpu_start, "s")


sensorVis.finish()

thread.join()

