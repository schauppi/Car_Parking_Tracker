import cv2
import pickle
import numpy as np
import math

width, height = 25, 80
angle = 62

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)



def rotate_rect(origin, point, angle):

    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return int(qx), int(qy)


while True:
    img = cv2.imread("parking_lot.jpeg")
    for pos in posList:
        #cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
        pos1 = pos
        pos2 = pos[0] + 0, pos[1] + height
        pos3 = pos[0] + width, pos[1] + height
        pos4 = pos[0] + width, pos[1] + 0
        cx = int(pos1[0] + ((pos3[0] - pos1[0]) / 2))
        cy = int(pos1[1] + ((pos3[1] - pos1[1]) / 2))

        pos_array = np.array([pos1, pos2, pos3, pos4])

        #center point
        p_m = pos1[0] + 25, pos1[1] +25
        #transform points
        p1_rot = rotate_rect(p_m, pos1, angle)
        p2_rot = rotate_rect(p_m, pos2, angle)
        p3_rot = rotate_rect(p_m, pos3, angle)
        p4_rot = rotate_rect(p_m, pos4, angle)

        trans_array = np.array([p1_rot, p2_rot, p3_rot, p4_rot])

        cv2.drawContours(img, [trans_array], 0, (155, 155, 155), 2, cv2.LINE_AA)
        #cv2.circle(img, p_m, 10, (255, 0, 0), 2)
        #cv2.circle(img, p1_rot, 10, (255, 0, 0), 2)
        #cv2.circle(img, p2_rot, 10, (255, 0, 0), 2)
        #cv2.circle(img, p3_rot, 10, (255, 0, 0), 2)
        #cv2.circle(img, p4_rot, 10, (255, 0, 0), 2)


    #cv2.circle(img, p0, 10, (255,0,0), 2)
    #cv2.drawContours(img, [rect_angle], 0, (155, 155, 155), -1, cv2.LINE_AA)
    #cv2.drawContours(img, [p], 0, (155, 155, 155), -1, cv2.LINE_AA)
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    cv2.waitKey(1)

