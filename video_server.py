import socket
import cv2
import numpy


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

TCP_IP = ''
TCP_PORT = 5001
while True:
    print("Waiting")
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    s.bind((TCP_IP, TCP_PORT))
    s.listen(True)
    conn, addr = s.accept()

    cv2.namedWindow('SERVER')
    
    print("Connected")
    while True:
        
        length = recvall(conn,16)
        if not length:
            break;
        stringData = recvall(conn, int(length))
        if not length:
            break;
        data = numpy.fromstring(stringData, dtype='uint8')
        decimg=cv2.imdecode(data,1)
        cv2.imshow('SERVER',decimg)
        cv2.waitKey(5)

    s.close()
    cv2.destroyWindow('SERVER')
