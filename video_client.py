#!/usr/bin/python

import socket
import cv2
import numpy
import time
import threading



# Parameters
TCP_IP = '10.16.10.123'
PORT = 5001

BALL_MIN_HUE = 75
BALL_MAX_HUE = 130
BALL_MIN_SAT = 127
BALL_MAX_SAT = 255
BALL_MIN_VAL = 32
BALL_MAX_VAL = 240
PRINT_BALL_COORDS = True
MARK_BALL = True
BALL_COLOR = (255, 0, 0)

PLAT_MIN_VAL = 63
PLAT_MAX_VAL = 255
PLAT_MIN_SAT = 0
PLAT_MAX_SAT = 63
PRINT_PLAT_COORDS = False
MARK_PLAT = False
PLAT_COLOR = (0, 0, 255)

ERODE_KERNEL_SIZE = 5

JPEG_QUALITY = 90

PRINT_TIMES = False
PRINT_FPS = False

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


def timepoint(name):
    ms = int(round(time.time() * 1000))
    delta = ms - timepoint.lastTime
    timepoint.lastTime = ms
    times[name] = delta
times = {}
timepoint.lastTime = 0

def sendFrame():
    print("Connecting to " + TCP_IP + ":" + str(PORT))
    sock = socket.socket()
    sock.connect((TCP_IP, PORT))
    print("Connected")
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
    while sendFrame.run:
        if sendFrame.frame is not None:
            outputFrame = sendFrame.frame
            sendFrame.frame = None

            result, imgencode = cv2.imencode('.jpg', outputFrame, encode_param)
            data = numpy.array(imgencode)
            stringData = data.tostring()

            print("Sending frame " + str(sendFrame.number))

            sock.send( str(len(stringData)).ljust(16));
            sock.send( stringData);

        time.sleep(1.01)
    sock.shutdown(2)
    sock.close()
sendFrame.frame = None        
sendFrame.number = 0
sendFrame.run = True


# Setup camera
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Camera not open")
    exit()

cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# Start Network thread
tcpThread = threading.Thread(target = sendFrame)
tcpThread.start()


frameCount = 0
try:
    while True:
        frameStart = int(round(time.time() * 1000))
        times = {}
        timepoint("Start")

        ret, frame = cam.read()
        timepoint("Capture")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        [hue, sat, val] = cv2.split(hsv)
        timepoint("ToHSV")
        
        kernel = numpy.ones((ERODE_KERNEL_SIZE, ERODE_KERNEL_SIZE),numpy.uint8)

        #Detect the blue ball
        blue = cv2.inRange(hue, BALL_MIN_HUE, BALL_MAX_HUE)
        saturated = cv2.inRange(sat, BALL_MIN_SAT, BALL_MAX_SAT)
        mediumLightness = cv2.inRange(val, BALL_MIN_VAL, BALL_MAX_VAL)
        ball = cv2.bitwise_and(blue, saturated)
        ball = cv2.bitwise_and(ball, mediumLightness)
        ball = cv2.erode(ball, kernel, iterations = 1)
        timepoint("FindBall")
        
#        # Detect the white-ish platform
#        light = cv2.inRange(val, PLAT_MIN_VAL, PLAT_MAX_VAL)
#        unsaturated = cv2.inRange(sat, PLAT_MIN_SAT, PLAT_MAX_SAT)
#        platform = cv2.bitwise_and(light, unsaturated)
#        platform = cv2.erode(platform, kernel, iterations = 1)

#        contours, hierarchy = cv2.findContours(platform, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#        if len(contours) > 0:
#            x,y,w,h = cv2.boundingRect(contours[0])
#        timepoint("FindPlatform")
#        if PRINT_PLAT_COORDS:
#            print("x: " + str(x) + " y: " + str(y) + " w: " + str(w) + " h: " + str(h))
#            timepoint("PrintPlatform")

        moments = cv2.moments(ball)
#        outputFrame = frame
#        outputFrame = cv2.bitwise_and(frame, frame, mask=ball)
#        outputFrame = platform

#        if MARK_PLAT:
#            cv2.rectangle(outputFrame, (x,y), (x+w,y+h), PLAT_COLOR, 2)
#            timepoint("MarkPlatform")

        if moments['m00'] != 0:
            xRaw = int(moments['m10'] / moments['m00'])
            yRaw = int(moments['m01'] / moments['m00'])

            xBall = (xRaw - x) / (1.0 * w) * 2 - 1;
            yBall = (yRaw - y) / (1.0 * h) * 2 - 1; 

            if PRINT_BALL_COORDS:
                if w > FRAME_WIDTH / 2 and h > FRAME_HEIGHT / 2:
                    print("x: " + "{:.3f}".format(xBall) + "\ty: " + "{:.3f}".format(yBall))
                    timepoint("PrintBall")
                else:
                    print("Frame is too small")

            if MARK_BALL:
                cv2.circle(outputFrame, (xRaw, yRaw), 16, BALL_COLOR, -1)

                timepoint("MarkBall")

        sendFrame.number = frameCount
        sendFrame.frame = outputFrame

        if PRINT_TIMES:
            print(times)

        frameCount = frameCount + 1

        if PRINT_FPS:
            frameDelta = int(round(time.time() * 1000)) - frameStart
            print(str(1000 / frameDelta) + " FPS")

except KeyboardInterrupt:
    pass

sendFrame.run = False

print("Exiting")

