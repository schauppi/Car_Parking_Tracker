import getopt
import math
import pickle
import sys
import time
import operator
import cv2
import numpy as np

RAW_IMAGE_DIRECTORY = '../data/raw/'
PROCESSED_IMAGE_DIRECTORY = '../data/processed/'

positionList = None
imgOffsetX = 0

width, height = 25, 80
angle = 62


def transformParkingSpace(position, positionCenter):
    positionTopLeft = position
    positionBottomLeft = position[0], positionTopLeft[1] + height
    positionBottomRight = position[0] + width, position[1] + height
    positionTopRight = position[0] + width, position[1]

    rotatedPositionTopLeft = rotateRect(positionCenter, positionTopLeft, angle)
    rotatedPositionBottomLeft = rotateRect(positionCenter, positionBottomLeft, angle)
    rotatedPositionBottomRight = rotateRect(positionCenter, positionBottomRight, angle)
    rotatedPositionTopRight = rotateRect(positionCenter, positionTopRight, angle)

    transformedArray = np.array(
        [rotatedPositionTopLeft, rotatedPositionBottomLeft, rotatedPositionBottomRight, rotatedPositionTopRight])

    return transformedArray


def rotateRect(origin, point, angle):
    angle = math.radians(angle)
    originX, originY = origin
    pointX, pointY = point

    qx = originX + math.cos(angle) * (pointX - originX) - math.sin(angle) * (pointY - originY)
    qy = originY + math.sin(angle) * (pointX - originX) + math.cos(angle) * (pointY - originY)

    return int(qx), int(qy)


def getPolygonCenter(polygon):
    xSum = 0
    ySum = 0

    for point in polygon:
        xSum += point[0]
        ySum += point[1]

    x = int(xSum / len(polygon))
    y = int(ySum / len(polygon))

    return (x, y)


def getPolygonBounds(polygon):
    xMax = max(polygon, key=operator.itemgetter(0))[0]
    xMin = min(polygon, key=operator.itemgetter(0))[0]
    yMax = max(polygon, key=operator.itemgetter(1))[1]
    yMin = min(polygon, key=operator.itemgetter(1))[1]

    return (xMin, yMin, xMax, yMax)


def checkParkingSpace(preparedImage, image, outputFilename):
    spaceCounter = 0

    for i, position in enumerate(positionList):
        positionCenter = getPolygonCenter(position)
        positionBounds = getPolygonBounds(position)
        positionArray = np.array(position)

        # cv2.polylines(image, [positionArray], True, (155, 155, 155), 2, cv2.LINE_AA)
        mask = np.zeros_like(preparedImage)
        cv2.fillPoly(mask, [positionArray], (255, 255, 255))
        out = cv2.bitwise_and(preparedImage, preparedImage, mask=mask)
        croppedOut = out[positionBounds[1]:positionBounds[3], positionBounds[0]:positionBounds[2]]

        whitePixelCount = cv2.countNonZero(croppedOut)
        totalPixelCount = croppedOut.shape[0] * croppedOut.shape[1]
        whitePixelRatio = whitePixelCount / totalPixelCount

        cv2.putText(image, str('%.2f' % whitePixelRatio), positionCenter, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255))

        if whitePixelRatio < 0.2:
            color = (0, 255, 0)
            thickness = 1
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 3

        cv2.polylines(image, [positionArray], True, color, thickness, cv2.LINE_AA)

    cv2.putText(image, f"Free: {spaceCounter}/{len(positionList)}", (int(image.shape[0] / 2), int(image.shape[1] / 2)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0))

    print(f'{spaceCounter}/{len(positionList)}')
    cv2.imwrite(PROCESSED_IMAGE_DIRECTORY + outputFilename, image)


def prepareImage(image):
    grayscaledImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurredImage = cv2.GaussianBlur(grayscaledImage, (3, 3), 1)
    shapedImage = cv2.adaptiveThreshold(blurredImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 45,
                                        16)
    medianImage = cv2.medianBlur(shapedImage, 5)
    kernel = np.ones((5, 5), np.uint8)
    dilatedImage = cv2.dilate(medianImage, kernel, iterations=1)

    return dilatedImage


def extractCmdArguments():
    positionListFileName = ''
    leftInputFileName = ''
    rightInputFileName = ''
    stitchedOutputFileName = ''
    processedOutputFileName = ''
    shouldBeCropped = False

    try:
        opts = getopt.getopt(sys.argv[1:], 'l:r:s:o:i:c')[0]
    except Exception as err:
        print(err, file=sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-l':
            leftInputFileName = arg
        elif opt == '-r':
            rightInputFileName = arg
        elif opt == '-s':
            stitchedOutputFileName = arg
        elif opt == '-o':
            processedOutputFileName = arg
        elif opt == '-i':
            positionListFileName = arg
        elif opt == '-c':
            shouldBeCropped = True
    if ((not leftInputFileName) or (not rightInputFileName) or (not stitchedOutputFileName) or (
            not processedOutputFileName) or (not positionListFileName)):
        print('Not all required options were provided', file=sys.stderr)
        sys.exit(2)
    return leftInputFileName, rightInputFileName, stitchedOutputFileName, processedOutputFileName, positionListFileName, shouldBeCropped


def stitchImages(leftImageName, rightImageName, stichedImageName):
    leftImage = cv2.imread(RAW_IMAGE_DIRECTORY + leftImageName)
    rightImage = cv2.imread(RAW_IMAGE_DIRECTORY + rightImageName)

    stitcher = cv2.Stitcher.create(cv2.STITCHER_PANORAMA)
    stitchedImage = stitcher.stitch([leftImage, rightImage])[1]
    if shouldBeCropped:
        stitchedImage = stitchedImage[900:stitchedImage.shape[0] - 200, imgOffsetX:stitchedImage.shape[1] - imgOffsetX]

    cv2.imwrite('../data/raw/' + stichedImageName, stitchedImage)

    return stitchedImage


def processImage(image, outputFilename):
    preparedImage = prepareImage(image)
    checkParkingSpace(preparedImage, image, outputFilename)


leftInputFileName, rightInputFileName, stitchedOutputFileName, processedOutputFileName, positionListFileName, shouldBeCropped = extractCmdArguments()
if shouldBeCropped:
    imgOffsetX = 1500

try:
    with open(positionListFileName, 'rb') as f:
        positionList = pickle.load(f)
except:
    positionList = []

stitchedImage = stitchImages(leftInputFileName, rightInputFileName, stitchedOutputFileName)
processImage(stitchedImage, processedOutputFileName)
