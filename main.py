import cv2
import pickle
import numpy as np
import math
import time

width, height = 25, 80
angle = 62

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

def rotate_rect(origin, point, angle):

    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return int(qx), int(qy)

def checkParkingSpace(imgPro, img):
    spaceCounter = 0
    for i, pos in enumerate(posList):
        x, y = pos
        pos1 = pos
        pos2 = pos[0] + 0, pos[1] + height
        pos3 = pos[0] + width, pos[1] + height
        pos4 = pos[0] + width, pos[1] + 0
        cx = int(pos1[0] + ((pos3[0] - pos1[0]) / 2))
        cy = int(pos1[1] + ((pos3[1] - pos1[1]) / 2))

        #center point
        p_m = pos1[0] + 25, pos1[1] +25
        #transform points
        p1_rot = rotate_rect(p_m, pos1, angle)
        p2_rot = rotate_rect(p_m, pos2, angle)
        p3_rot = rotate_rect(p_m, pos3, angle)
        p4_rot = rotate_rect(p_m, pos4, angle)

        trans_array = np.array([p1_rot, p2_rot, p3_rot, p4_rot])

        cv2.drawContours(img, [trans_array], 0, (155, 155, 155), 2, cv2.LINE_AA)

        mask = np.zeros_like(imgPro)
        cv2.drawContours(mask, [trans_array], 0, (255, 255, 255), -1)
        out = np.zeros_like(imgPro)
        out[mask == 255] = imgPro[mask == 255]


        count = cv2.countNonZero(out)
        cv2.putText(img,str(count), (p_m[0]-20,p_m[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
        #cv2.imwrite(f"test{count}.png", out)

        if count < 150:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.drawContours(img, [trans_array], 0, color, thickness, cv2.LINE_AA)
    cv2.putText(img, f"Free: {spaceCounter}/{len(posList)}", (int(img.shape[0]/2), int(img.shape[1]/2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0))


while True:
    img = cv2.imread("parking_lot.jpeg")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    checkParkingSpace(imgDilate, img)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    time.sleep(5)

