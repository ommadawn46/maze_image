#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import BytesIO
from PIL import Image
import socket
import base64
import time

# makeImageMaker
#    wallSize == 1 and pathSize == 1 のときのみ動作可能

HOST = '127.0.0.1'
PORT = 54321
BUFSIZE = 1 << 12

def imageToMaze(img):
    maze = [[1]*img.size[0] for _ in [0]*img.size[1]]
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            px = img.getpixel((x, y))
            if px == (255, 255, 255):
                maze[y][x] = 0
            elif px == (0, 0, 0):
                maze[y][x] = 1
            elif px == (255, 0, 0):
                maze[y][x] = 8
                startPoint = (y, x)
            elif px == (0, 0, 255):
                maze[y][x] = 9
    return (startPoint, maze)

DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
def searchRoute(sy, sx, maze):
    queue = [(sy, sx, [])]
    while len(queue) > 0:
        y, x, route = queue.pop(0)
        if not (0 <= y < len(maze) and 0 <= x < len(maze[0])) or maze[y][x] == 1 or (x, y) in route:
            continue
        route.append((x, y))
        if maze[y][x] == 9:
            return route
        for d in DIRS:
            queue.append((y+d[1], x+d[0], route[:]))

def setRoute(img, route):
    for p in route[1:-1]:
        img.putpixel(p, (0, 255, 0))

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    while True:
        recved = ''
        st = time.time()
        while not '>' in recved:
            recved += s.recv(BUFSIZE).decode('utf-8')
            if time.time() - st > 10:
                break
        print(recved)
        imgBin = base64.b64decode(recved.split('base64,')[1].split('">')[0])
        img = Image.open(BytesIO(imgBin))
        sp, maze = imageToMaze(img)
        route = searchRoute(sp[0], sp[1], maze)
        setRoute(img, route)
        img.show()
        bio = BytesIO()
        img.save(bio, "png")
        s.sendall(b'<img src="data:image/png;base64,' + base64.b64encode(bio.getvalue()) + b'">')

    s.close()

if __name__ == '__main__':
    main()
