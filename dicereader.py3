# Dice Reader
# Allen Snook
# March 6, 2021

# Based on https://golsteyn.com/projects/dice/ by Quentin Golsteyn
# Requires opencv-python numpy

import cv2
import numpy as np

# Setting up the blob detector
params = cv2.SimpleBlobDetector_Params()
params.filterByInertia
params.minInertiaRatio = 0.6
detector = cv2.SimpleBlobDetector_create(params)

def getBlobs(frame):
    frameBlurred = cv2.medianBlur(frame, 7)
    frameGray = cv2.cvtColor(frameBlurred, cv2.COLOR_BGR2GRAY)
    blobs = detector.detect(frameGray)
    print("found # of blobs:", len(blobs))
    return blobs

def overlay_info(frame, blobs):
    # Overlay blobs
    for b in blobs:
        pos = b.pt
        r = b.size / 2

        cv2.circle(frame, (int(pos[0]), int(pos[1])),
                   int(r), (255, 0, 0), 2)

def countPipsInImage(imagePath):
    # Open the image
    image = cv2.imread(imagePath)
    imageHeight, imageWidth, imageColorPlanes = image.shape

    cropX1 = int(0.35 * imageWidth)
    cropX2 = int(0.67 * imageWidth)
    cropY1 = int(0.3 * imageHeight)
    cropY2 = int(0.7 * imageHeight)

    # Crop the image
    croppedImage = image[cropY1:cropY2, cropX1:cropX2]

    # Count the pips
    blobs = getBlobs(croppedImage)

    # Out the overlay
    overlay_info(croppedImage, blobs)

    # Save the result for later reference
    cv2.imwrite('./processed.png', croppedImage)

    # Debugging: Show the result
    # cv2.imshow('img', croppedImage)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return len(blobs)

imagePath = "./image.jpg"
print("image_path:", imagePath)
pips = countPipsInImage(imagePath)
print("pips: ", pips)
