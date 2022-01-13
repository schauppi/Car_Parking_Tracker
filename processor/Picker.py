import cv2
import pickle
import numpy as np
import sys
import getopt

newPosition = []
positionList = None
imgOffsetX = 0


def extractCmdArguments():
    positionListFileName = ''
    imageFileName = ''
    shouldBeCropped = False

    try:
        opts = getopt.getopt(sys.argv[1:], 'l:i:c')[0]
    except Exception as err:
        print(err, file=sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-l':
            positionListFileName = arg
        elif opt == '-i':
            imageFileName = arg
        elif opt == '-c':
            shouldBeCropped = True
    if ((not imageFileName) or (not positionListFileName)):
        print('Not all required options were provided', file=sys.stderr)
        sys.exit(2)

    return positionListFileName, imageFileName, shouldBeCropped


def isPointInsidePolygon(point, polygon):
    n = len(polygon)
    x = point[0]
    y = point[1]
    isInside = False
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        isInside = not isInside
        p1x, p1y = p2x, p2y

    return isInside


def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        global newPosition, positionListFileName
        newPosition.append((x, y))

        if len(newPosition) == 4:
            positionList.append(newPosition)
            newPosition = []
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, position in enumerate(positionList):
            if isPointInsidePolygon((x, y), position):
                positionList.pop(i)

    with open(positionListFileName, 'wb') as f:
        pickle.dump(positionList, f)


positionListFileName, imageFileName, shouldBeCropped = extractCmdArguments()
try:
    with open(positionListFileName, 'rb') as f:
        positionList = pickle.load(f)
except:
    positionList = []

if shouldBeCropped:
    imgOffsetX = 1500
    for position in positionList:
        for i, point in enumerate(position):
            position[i] = (point[0] - imgOffsetX, point[1])

while True:
    img = cv2.imread(imageFileName)
    if shouldBeCropped:
        img = img[900:img.shape[0] - 200, imgOffsetX:img.shape[1] - imgOffsetX]

    for position in positionList:
        positionPolygon = np.array(position)
        cv2.polylines(img, [positionPolygon], True, (66, 135, 245), 2, cv2.LINE_AA)

    if len(newPosition) == 1:
        cv2.circle(img, newPosition[0], 1, (255, 255, 255), 2, cv2.LINE_AA)
    elif len(newPosition) > 1:
        polygonLines = np.array(newPosition)
        cv2.polylines(img, [polygonLines], False, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    cv2.waitKey(1)
