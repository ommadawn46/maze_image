#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import random, shuffle
from PIL import Image

DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRDIC = {(0, 2): 0, (2, 0):1, (0, -2):2, (-2, 0):3}


class MazeNode():
    def __init__(self, y, x, depth, parent=None):
        self.y = y
        self.x = x
        self.depth = depth
        self.parent = parent
        self.childs = []
        self.route = [self]


def findLingestPath(maze):
    """迷路から最も距離の長い2点を見つける"""
    sy, sx = len(maze)//2, len(maze[0])//2 + 1
    sy += 1 if sy % 2 == 0 else 0
    sx += 1 if sx % 2 == 0 else 0
    root = MazeNode(sy, sx, 0)
    stack = [root]
    depthNodes = [[root]]
    while len(stack) > 0:
        mn = stack.pop()
        x, y = mn.x, mn.y
        for d in DIRS:
            ix, iy = x + d[0], y + d[1]
            nx, ny = x + d[0]*2, y + d[1]*2
            if mn.parent != None and ny == mn.parent.y and nx == mn.parent.x:
                continue
            if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]):
                if maze[iy][ix] == 0:
                    nmn = MazeNode(ny, nx, mn.depth+1, mn)
                    stack.append(nmn)
                    mn.childs.append(nmn)
                    if len(depthNodes) <= nmn.depth:
                        depthNodes.append([nmn])
                    else:
                        depthNodes[nmn.depth].append(nmn)
    maxdepth = len(depthNodes)-1
    maxlength = -1
    maxroute = None
    for depth in reversed(range(len(depthNodes))):
        for mn in depthNodes[depth]:
            if len(mn.childs) == 1:
                mn.route += mn.childs[0].route
            elif len(mn.childs) > 1:
                mn.childs.sort(key = lambda c: len(c.route))
                fc, sc = mn.childs[-1], mn.childs[-2]
                fl, sl = len(fc.route), len(sc.route)
                mn.route += fc.route
                if maxlength < fl + sl + 1:
                    maxlength = fl + sl + 1
                    maxroute = list(reversed(fc.route)) + [mn]
                    maxroute.extend(sc.route)
    if maxlength < maxdepth:
        maxlength = maxdepth
        maxroute = root.route
    return maxroute


def setLongestPath(maze):
    """端点の設定"""
    maxroute = findLingestPath(maze)
    startSetted = False
    py = px = -1
    for mn in maxroute:
        if len(mn.childs) <= 0 or (mn.parent == None and len(mn.childs) <= 1):
            if startSetted:
                maze[mn.y][mn.x] = 8
            else:
                maze[mn.y][mn.x] = 9
                startSetted = True
        else:
            maze[mn.y][mn.x] = 7
        if px != -1 and py != -1:
            maze[(mn.y+py)//2][(mn.x+px)//2] = 7
        py, px = mn.y, mn.x


def makeRawMaze(row, col):
    """迷路を作成する"""
    row += 1 if row % 2 == 0 else 0
    col += 1 if col % 2 == 0 else 0
    maze = [[1]*col for _ in [0]*row]
    sy, sx = int(random()*(row//2))*2 + 1, int(random()*(col//2))*2 + 1
    maze[sy][sx] = 0
    dirs = DIRS[:]
    shuffle(dirs)
    stack = [(sy, sx, d) for d in dirs]
    while len(stack) > 0:
        y, x, d = stack.pop()
        ix, iy = x + d[0], y + d[1]
        nx, ny = x + d[0]*2, y + d[1]*2
        if 0 <= ny < len(maze) and 0 <= nx < len(maze[0]):
            if maze[ny][nx] == 1:
                maze[iy][ix] = maze[ny][nx] = 0
                shuffle(dirs)
                for d in dirs:
                    stack.append((ny, nx, d))
    return maze


def makeMaze(row, col):
    """迷路の作成し，端点を設定する"""
    maze = makeRawMaze(row, col)
    setLongestPath(maze)
    return maze


def mazeToImages(maze, wallSize = 1, pathSize = 1):
    """迷路をPIL画像にする"""
    width = wallSize*int(len(maze[0])/2 + 1) + pathSize*int(len(maze[0])/2)
    height = wallSize*int(len(maze)/2 + 1) + pathSize*int(len(maze)/2)
    problem = Image.new("RGB", (width, height), (0,0,0))
    solution = Image.new("RGB", (width, height), (0,0,0))
    p_pixs = problem.load()
    s_pixs = solution.load()
    cy = 0
    for y in range(len(maze)):
        cx = 0
        for x in range(len(maze[0])):
            if maze[y][x] == 0:
                # 通路
                for dx in range(pathSize):
                    for dy in range(pathSize):
                        p_pixs[cx+dx,cy+dy] = s_pixs[cx+dx,cy+dy] = (255,255,255)
            elif maze[y][x] == 1:
                # 壁
                for dx in range(wallSize):
                    for dy in range(wallSize):
                        p_pixs[cx+dx,cy+dy] = s_pixs[cx+dx,cy+dy] = (0, 0, 0)
            elif maze[y][x] == 7:
                # 正解経路
                for dx in range(pathSize):
                    for dy in range(pathSize):
                        p_pixs[cx+dx,cy+dy] = (255,255,255)
                        s_pixs[cx+dx,cy+dy] = (0, 255, 0)
            elif maze[y][x] == 8:
                # 端点A
                for dx in range(pathSize):
                    for dy in range(pathSize):
                        p_pixs[cx+dx,cy+dy] = s_pixs[cx+dx,cy+dy] = (0, 0, 255)
            elif maze[y][x] == 9:
                # 端点B
                for dx in range(pathSize):
                    for dy in range(pathSize):
                        p_pixs[cx+dx,cy+dy] = s_pixs[cx+dx,cy+dy] = (255, 0, 0)
            if x % 2 == 0:
                cx += wallSize
            else:
                cx += pathSize
        if y % 2 == 0:
            cy += wallSize
        else:
            cy += pathSize
    return (problem, solution)


def compMazeImage(img1, img2):
    if img1.size != img2.size:
        return False
    pixs1 = img1.load()
    pixs2 = img2.load()
    for x in range(img1.size[0]):
        for y in range(img1.size[1]):
            for i in range(3):
                if (pixs1[x, y][i] < 255//2) != (pixs2[x, y][i] < 255//2):
                    return False
    return True


def main():
    row, col = 180, 320
    maze = makeMaze(row, col)
    problem, solution = mazeToImages(maze)
    problem.show()
    solution.show()
    #problem.save('problem%dx%d.png' % (row, col), compress_level = 9)
    #solution.save('solution%dx%d.png' % (row, col), compress_level = 9)


if __name__ == '__main__':
    main()
