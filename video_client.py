#!/usr/bin/python

import socket
import cv2
import numpy
import time
import threading



# Parameters
TCP_IP = '10.16.10.123'
PORT = 5001

BALL_MIN_HUE = 0
BALL_MAX_HUE = 10 
BALL_MIN_SAT = 127
BALL_MAX_SAT = 255
BALL_MIN_VAL = 63
BALL_MAX_VAL = 255
PRINT_BALL_COORDS = False
PRINT_BALL_PIXEL_COORDS = False
MARK_BALL = False
BALL_COLOR = (0, 0, 255)
MASK_IMAGE = True

ERODE_KERNEL_SIZE = 3

JPEG_QUALITY = 50

PRINT_TIMES = False
PRINT_FPS = True

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

run = True

def timepoint(name):
    ms = int(round(time.time() * 1000))
    delta = ms - timepoint.lastTime
    timepoint.lastTime = ms
    times[name] = delta
times = {}
timepoint.lastTime = 0

def sendFrame():
    global run
    try:
        print("Connecting to " + TCP_IP + ":" + str(PORT))
        sock = socket.socket()
        sock.connect((TCP_IP, PORT))
        print("Connected")
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        while run:
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
    except KeyboardInterrupt:
        pass
    run = False
sendFrame.frame = None        
sendFrame.number = 0

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

edgeFile = open('edges.txt', 'r')
if edgeFile:
    edges = edgeFile.read().split()
    edgeX0 = int(edges[0])
    edgeX1 = int(edges[1])
    edgeY0 = int(edges[2])
    edgeY1 = int(edges[3])
    print("Read edges.txt:")
    print(edges[:4])

def Edge(name):
    if name is "top-left":
        edgeX0 = xRaw
        edgeY0 = yRaw
    if name is "bottom-right":
        edgeX1 = xRaw
        edgeY1 = yRaw
    else:
        print("Edge: bad name")

def captureLoop():
    global run
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("Camera not open")
            exit()

        cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        while run:
            if captureLoop.newFrame is None:
                ret, f = cam.read()
                captureLoop.newFrame = f
            time.sleep(0.001)
        cam.release()
    except KeyboardInterrupt:
        pass
    run = False
captureLoop.newFrame = None

def processLoop():
    global frameCount 
    global run
    try:
        while run:
            frameStart = int(round(time.time() * 1000))
            times = {}
            timepoint("Start")

#        ret, frame = cam.read()
#        timepoint("Capture")
        
            if captureLoop.newFrame is None:
                time.sleep(0.001)
                continue
            frame = captureLoop.newFrame
            captureLoop.newFrame = None

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
                    print("x: " + "{:.3f}".format(xBall) + "\ty: " + "{:.3f}".format(yBall))
                    timepoint("PrintBall")
                if PRINT_BALL_PIXEL_COORDS:
                    print("xRaw: " + str(xRaw) + "\tyRaw: " + str(yRaw))

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

    run = False

    print("Exiting")


if __name__ == "__main__":
 
    # Start Network thread
    tcpThread = threading.Thread(target = sendFrame)
    tcpThread.start()   
    processThread = threading.Thread(target = processLoop)
    processThread.start()
    captureLoop()


