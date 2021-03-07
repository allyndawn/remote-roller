# Dice Reader
# Allen Snook
# March 6, 2021

# Based heavily on https://golsteyn.com/projects/dice/ by Quentin Golsteyn
# Requires opencv-python numpy sklearn

import cv2
import numpy as np
from sklearn import cluster

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

def getDiceFromBlobs(blobs):
    # Get centroids of all blobs
    X = []
    for b in blobs:
        pos = b.pt

        if pos != None:
            X.append(pos)

    X = np.asarray(X)

    if len(X) > 0:
        # Important to set min_sample to 0, as a dice may only have one dot
        clustering = cluster.DBSCAN(eps=40, min_samples=0).fit(X)

        # Find the largest label assigned + 1, that's the number of dice found
        numDice = max(clustering.labels_) + 1

        dice = []

        # Calculate centroid of each dice, the average between all a dice's dots
        for i in range(numDice):
            X_dice = X[clustering.labels_ == i]

            centroid_dice = np.mean(X_dice, axis=0)

            dice.append([len(X_dice), *centroid_dice])

        return dice

    else:
        return []

def overlay_info(frame, dice, blobs):
    # Overlay blobs
    for b in blobs:
        pos = b.pt
        r = b.size / 2

        cv2.circle(frame, (int(pos[0]), int(pos[1])),
                   int(r), (255, 0, 0), 2)

    # Overlay dice number
    for d in dice:
        # Get textsize for text centering
        textsize = cv2.getTextSize(
            str(d[0]), cv2.FONT_HERSHEY_PLAIN, 4, 4)[0]

        cv2.putText(frame, str(d[0]),
                    (int(d[1] - 50 - textsize[0] / 2),
                     int(d[2] - 50 + textsize[1] / 2)),
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)


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
    dice = getDiceFromBlobs(blobs)
    # print(dice)

    # Out the overlay
    overlay_info(croppedImage, dice, blobs)

    # Sum
    sum = 0
    for die in dice:
        sum += die[0]

    # Save the result for later reference
    cv2.imwrite('./processed.png', croppedImage)

    # Debugging: Show the result
    # cv2.imshow('img', croppedImage)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return sum

imagePath = "./playertwo.jpg"
print("image_path:", imagePath)
pips = countPipsInImage(imagePath)
print("pips: ", pips)
