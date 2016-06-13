#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import random
from io import BytesIO
from PIL import Image
import re
import math
import base64
import socket
import threading
import mazeImageMaker as mim

HOST = '0.0.0.0'
PORT = 54321
BUFSIZE = 1 << 12
BACKLOG = 10

SOCKETS = set()

class MazeThread(threading.Thread):
    def __init__(self, c, probremN = 10):
        threading.Thread.__init__(self)
        self.c = c
        self.probremN = probremN
        self.srow = self.scol = 11
        self.erow = self.ecol = 151
        self.c.settimeout(60)

    def close(self):
        print(str(self.c.getpeername()) + " is closed")
        self.c.close()
        SOCKETS.remove(self.c)

    def run(self):
        try:
            rowd = (self.erow - self.srow) / (self.probremN-1)
            cold = (self.ecol - self.scol) / (self.probremN-1)
            count = 0
            while count < self.probremN:
                row = self.srow + int(rowd * count)
                col = self.scol + int(cold * count)
                maze = mim.makeMaze(row, col)
                problem, solution = mim.mazeToImages(maze)
                bio = BytesIO()
                problem.save(bio, "png", compress_level = 9)
                self.c.sendall(b'<img src="data:image/png;base64,' + base64.b64encode(bio.getvalue()) + b'">\n')
                recved = ''
                while not '>' in recved:
                    recved += self.c.recv(BUFSIZE).decode('utf-8')
                pat = r'<img\s+src\s*=\s*"\s*data\s*:\s*image\s*/\s*png\s*;\s*base64\s*,(.*)"\s*>'
                try:
                    answerBin = base64.b64decode(re.sub(pat, r'\1', recved))
                except:
                    self.c.sendall(b"CAN'T DECODE IT AS A BASE64 STRING\n")
                    break
                try:
                    answer = Image.open(BytesIO(answerBin))
                    if not mim.compMazeImage(solution, answer):
                        self.c.sendall(b'INCORRECT ANSWER\n')
                        break
                except:
                    self.c.sendall(b"CAN'T OPEN IT AS AN IMAGE FILE\n")
                    break
                count += 1
            if count >= self.probremN:
                print(str(self.c.getpeername()) + " complete a game")
                self.c.sendall(b"CONGRATULATIONS!")
        except socket.timeout:
            self.c.sendall(b"TIME OUT\n")
        self.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SOCKETS.add(server)
    try:
        server.bind((HOST, PORT))
        server.listen(BACKLOG)
        while True:
            c, addr = server.accept()
            print("connected by " + str(addr))
            SOCKETS.add(c)
            MazeThread(c).start()
    finally:
        for s in SOCKETS:
            s.close()

if __name__ == '__main__':
    main()
