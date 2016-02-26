#!/usr/bin/python

import socket
import cv2
import numpy

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Camera not open")
    exit()

ret, frame = cam.read()

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

        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
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

