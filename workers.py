from threading import Thread
# import Robot_runner as rr
# import Image_processing as ip
# import CameraConfig
import time
import Xbox360

# Processor = ip.ProcessFrames(True)
def CreateThreads():
    #t1 = Thread(target = rr.Logic).start()
    #t2 = Thread(target = Processor.ProcessFrame).start()
    t3 = Thread(target = Xbox360.gamepad).start()
    time.sleep(2)
    t3.join()
    
CreateThreads()