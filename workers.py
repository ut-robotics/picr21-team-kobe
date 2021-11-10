from threading import Thread
import Robot_runner as rr
import Image_processing as ip
import CameraConfig

Processor = ip.ProcessFrames(True)

    
def CreateThreads():
    Thread(target = rr.Logic).start()
    Thread(target = Processor.ProcessFrame).start()
    
def StopThreads():
    Thread.join(rr.Logic)
    Thread.join(Processor.ProcessFrame)