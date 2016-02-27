#!/usr/bin/python

import socket
import cv2
import numpy

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Camera not open")
    exit()

TCP_IP = '10.16.10.123'
PORT = 5001

print("Connecting")
sock = socket.socket()
sock.connect((TCP_IP, PORT))
print("Connected")

encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]

frameCount = 0
try:
    while True:
        ret, frame = cam.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#        [red, green, blue] = cv2.split(frame)
        [hue, sat, val] = cv2.split(hsv)
        blue = cv2.inRange(hue, 75, 130)
        saturated = cv2.inRange(sat, 127, 255)
        ball = cv2.bitwise_and(blue, saturated)
#        print(cv2.moments(ball))
        moments = cv2.moments(ball)
        x = int(moments['m10'] / moments['m00'])
        y = int(moments['m01'] / moments['m00'])
        print("x: " + str(x))
        print("y: " + str(y))

        outputFrame = frame
        cv2.circle(outputFrame, (x, y), 16, (255, 255, 255), -1)
#        outputFrame = ball
#        ret, val = cv2.threshold(val, 127, 255, cv2.THRESH_BINARY)
#        outputFrame = cv2.merge([hue, sat, val])       
#        outputFrame = cv2.cvtColor(outputFrame, cv2.COLOR_HSV2BGR)
#        ret, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)
#        ret, green = cv2.threshold(green, 127, 255, cv2.THRESH_BINARY_INV)
#        ret, blue = cv2.threshold(blue, 127, 255, cv2.THRESH_BINARY)

#        outputFrame = cv2.merge([red, green, blue])
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #ret, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

        result, imgencode = cv2.imencode('.jpg', outputFrame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()

        print("Sending frame " + str(frameCount))
        frameCount = frameCount + 1

        sock.send( str(len(stringData)).ljust(16));
        sock.send( stringData);
except KeyboardInterrupt:
    pass

sock.shutdown(2)
sock.close()
print("Exiting")

