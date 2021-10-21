import cv2


def CreateDetector():
    blobparams = cv2.SimpleBlobDetector_Params()
    blobparams.minDistBetweenBlobs = 50
    blobparams.filterByCircularity = False
    blobparams.filterByArea = True
    blobparams.minArea = 25#255
    blobparams.maxArea = 100000000
    blobparams.filterByInertia = False
    blobparams.filterByConvexity = False
    detector = cv2.SimpleBlobDetector_create(blobparams)
    return detector