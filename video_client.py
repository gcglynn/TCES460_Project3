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
MASK_IMAGE = False 

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

xRaw = 0
yRaw = 0
xBall = 0
yBall = 0
def getBallPos():
    return (xBall, yBall)

frameCount = 0
def getFrameNumber():
    return frameCount

edgeX0 = 0
edgeX1 = FRAME_WIDTH
edgeY0 = 0
edgeY1 = FRAME_HEIGHT
def Edge(name):
    if name is "top-left":
        edgeX0 = xRaw
        edgeY0 = yRaw
    if name is "bottom-right":
        edgeX1 = xRaw
        edgeY1 = yRaw
    else:
        print("Edge: bad name")

# Setup camera
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Camera not open")
    exit()

cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)


def captureLoop():
  global frameCount 
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
        
        moments = cv2.moments(ball)

        if MASK_IMAGE:
            outputFrame = cv2.bitwise_and(frame, frame, mask=ball)
        else:
            outputFrame = frame

        if moments['m00'] != 0:
            xRaw = int(moments['m10'] / moments['m00'])
            yRaw = int(moments['m01'] / moments['m00'])

            xBall = (xRaw - edgeX0) / (1.0 * edgeX1 - edgeX0) * 2 - 1;
            yBall = (yRaw - edgeY0) / (1.0 * edgeY1 - edgeY0) * 2 - 1; 

            if PRINT_BALL_COORDS:
#                if w > FRAME_WIDTH / 2 and h > FRAME_HEIGHT / 2:
                    print("x: " + "{:.3f}".format(xBall) + "\ty: " + "{:.3f}".format(yBall))
                    timepoint("PrintBall")
#                else:
#                    print("Frame is too small")

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


if __name__ == "__main__":
 
    # Start Network thread
    tcpThread = threading.Thread(target = sendFrame)
    tcpThread.start()   
    captureLoop()


