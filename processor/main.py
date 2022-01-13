import cv2
import pickle
import numpy as np
import math
import sys
import getopt

RAW_IMAGE_DIRECTORY = '../data/raw/'
PROCESSED_IMAGE_DIRECTORY = '../data/processed/'

posList = None
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


def checkParkingSpace(preparedImage, image, outputFilename):
    global posList
    spaceCounter = 0

    for i, pos in enumerate(posList):
        positionCenter = pos[0] + 25, pos[1] + 25
        transformedArray = transformParkingSpace(pos, positionCenter)

        cv2.drawContours(image, [transformedArray], 0, (155, 155, 155), 2, cv2.LINE_AA)
        mask = np.zeros_like(preparedImage)
        cv2.drawContours(mask, [transformedArray], 0, (255, 255, 255), -1)
        out = np.zeros_like(preparedImage)
        out[mask == 255] = preparedImage[mask == 255]
        count = cv2.countNonZero(out)
        cv2.putText(image, str(count), (positionCenter[0] - 20, positionCenter[1]), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255))

        if count < 150:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.drawContours(image, [transformedArray], 0, color, thickness, cv2.LINE_AA)
    cv2.putText(image, f"Free: {spaceCounter}/{len(posList)}", (int(image.shape[0] / 2), int(image.shape[1] / 2)),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0))
    # print(PROCESSED_IMAGE_DIRECTORY)
    # print(outputFilename)
    print(f'{spaceCounter}/{len(posList)}')
    cv2.imwrite(PROCESSED_IMAGE_DIRECTORY + outputFilename, image)
    # cv2.imshow("Image", image)
    # cv2.waitKey(1)
    # time.sleep(10)


def prepareImage(image):
    grayscaledImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurredImage = cv2.GaussianBlur(grayscaledImage, (3, 3), 1)
    shapedImage = cv2.adaptiveThreshold(blurredImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25,
                                        16)
    medianImage = cv2.medianBlur(shapedImage, 5)
    kernel = np.ones((3, 3), np.uint8)
    dilatedImage = cv2.dilate(medianImage, kernel, iterations=1)

    return dilatedImage


def extractCmdArguments():
    positionListFileName = ''
    leftInputFileName = ''
    rightInputFileName = ''
    stitchedOutputFileName = ''
    processedOutputFileName = ''

    try:
        opts = getopt.getopt(sys.argv[1:], 'l:r:s:o:i:')[0]
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
    if ((not leftInputFileName) or (not rightInputFileName) or (not stitchedOutputFileName) or (
            not processedOutputFileName) or (not positionListFileName)):
        print('Not all required options were provided', file=sys.stderr)
        sys.exit(2)
    return leftInputFileName, rightInputFileName, stitchedOutputFileName, processedOutputFileName, positionListFileName


def stitchImages(leftImageName, rightImageName, stichedImageName):
    leftImage = cv2.imread(RAW_IMAGE_DIRECTORY + leftImageName)
    rightImage = cv2.imread(RAW_IMAGE_DIRECTORY + rightImageName)

    stitcher = cv2.Stitcher.create(cv2.STITCHER_PANORAMA)
    stitchedImage = stitcher.stitch([leftImage, rightImage])[1]

    cv2.imwrite('../data/raw/' + stichedImageName, stitchedImage)

    return stitchedImage


def processImage(image, outputFilename):
    preparedImage = prepareImage(image)
    checkParkingSpace(preparedImage, image, outputFilename)


leftInputFileName, rightInputFileName, stitchedOutputFileName, processedOutputFileName, positionListFileName = extractCmdArguments()

try:
    with open(positionListFileName, 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

stitchedImage = stitchImages(leftInputFileName, rightInputFileName, stitchedOutputFileName)
processImage(stitchedImage, processedOutputFileName)
