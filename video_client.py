#!/usr/bin/python

import socket
import cv2
import numpy
import time
import threading
import servo_control

# Parameters
TCP_IP = '10.16.10.123'
PORT = 5001

BALL_MIN_HUE = 0
BALL_MAX_HUE = 30 
BALL_MIN_SAT = 127
BALL_MAX_SAT = 255
BALL_MIN_VAL = 63
BALL_MAX_VAL = 255
PRINT_BALL_COORDS = False
PRINT_BALL_PIXEL_COORDS = True
MARK_BALL = False
BALL_COLOR = (0, 0, 255)
MASK_IMAGE = True

ERODE_KERNEL_SIZE = 3

JPEG_QUALITY = 50

PRINT_TIMES = False
PRINT_FPS = False

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

ENABLE_SERVOS = True
PRINT_SERVOS = True

HOME = 1000
MAX = 500
MIN = 1500
SWAP_XY = True
INVERT_X = True
INVERT_Y = True

X_PIN = 3 #5
Y_PIN = 9 #6

X_DAMPENER = .45
Y_DAMPENER = .6

run = True
x_servo=None
y_servo=None
prev_xBall = 0
prev_yBall = 0

def timepoint(name):
    ms = int(round(time.time() * 1000))
    delta = ms - timepoint.lastTime
    timepoint.lastTime = ms
    times[name] = delta
times = {}
timepoint.lastTime = 0

def controller(xBall, yBall):
    global prev_xBall
    global prev_yBall
    if abs(xBall > 1):
	if xBall < 0:
		xBall = -1
	else:
		xBall = 1
    if abs(yBall > 1):
        if yBall < 0:
                yBall = -1
        else:
                yBall = 1
    x_range = (xBall+(xBall-prev_xBall)) * (MAX*X_DAMPENER)
    y_range = (yBall+(yBall-prev_yBall)) * (MAX*Y_DAMPENER)
    if x_range > 500:
    	x_range = 500
    if x_range < -500:
        x_range = -500
    if y_range > 500:
    	y_range = 500
    if y_range < -500:
    	y_range = -500
    x = int(x_range + HOME)
    y = int(y_range + HOME)
    prev_xBall = xBall
    prev_yBAll = yBall
    return x, y

def setupServos():
    global x_servo
    global y_servo
    print("STUB: setupServos()")
    x_servo = servo_control.init_servo(X_PIN, HOME)
    y_servo = servo_control.init_servo(Y_PIN, HOME)
    servo_control.init_axis(x_servo, y_servo, MIN, MAX)

def shutdownServos():
    global x_servo
    global y_servo   
    print("STUB: shutdownServos()")
    servo_control.tilt_neutral(x_servo, y_servo, HOME)
    #x_servo.enable(False)
    #y_servo.enable(False)

def setServos(x, y):
    global x_servo
    global y_servo     
    if PRINT_SERVOS:
        print("STUB: Updating servos to " + str(x) + ", " + str(y))
    if SWAP_XY:
        servo_control.tilt(x_servo, y)
        servo_control.tilt(y_servo, x)
    else:
        servo_control.tilt(x_servo, x)
        servo_control.tilt(y_servo, y)

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

frameCount = 0

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

if SWAP_XY:
    temp = edgeX0
    edgeX0 = edgeY0
    edgeY0 = temp
    temp = edgeX1
    edgeX1 = edgeY1
    edgeY1 = temp

if INVERT_X:
    temp = edgeX0
    edgeX0 = edgeX1
    edgeX1 = temp

if INVERT_Y:
    temp = edgeY0
    edgeY0 = edgeY1
    edgeY1 = temp

def captureLoop():
    global run
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("Camera not open")
            run = False
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
    global prev_xBall
    global prev_yBall
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

                if ENABLE_SERVOS:
                    xServo, yServo = controller(xBall, yBall)
                    setServos(xServo, yServo)

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
    shutdownServos()

    print("Exiting")


if __name__ == "__main__":
    if ENABLE_SERVOS:
        setupServos()
 
    # Start Network thread
    tcpThread = threading.Thread(target = sendFrame)
    tcpThread.start()   
    
    processThread = threading.Thread(target = processLoop)
    processThread.start()

    captureLoop()


