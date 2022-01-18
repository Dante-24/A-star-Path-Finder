import pygame as pg
from math import *
import heapq
from collections import *
import tkinter as tk

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

sze = 800
WIN = pg.display.set_mode((sze, sze))
pg.display.set_caption("Path Finder")

# The nodes representing spots on the grid
# either blocked, obstacle, open, start or end
class Node:
    def __init__(self, row, col, wid, tot_rows):
        self.row = row
        self.col = col
        self.x = row * wid
        self.y = col * wid
        self.color = WHITE
        self.neighb = []
        self.wid = wid
        self.tot_rows = tot_rows

    def getpos(self):
        return self.row, self.col

    def blocked(self):
        if self.color == RED:
            return True
        return False

    def isopen(self):
        if self.color == GREEN:
            return True
        return False

    def isobstacle(self):
        if self.color == BLACK:
            return True
        return False

    def isstart(self):
        if self.color == TURQUOISE:
            return True
        return False

    def isend(self):
        if self.color == PURPLE:
            return True
        return False

    def reset(self):
        self.color = WHITE

    def block(self):
        self.color = RED

    def open(self):
        self.color = GREEN

    def obstacle(self):
        self.color = BLACK

    def do_start(self):
        self.color = TURQUOISE

    def do_end(self):
        self.color = PURPLE

    def makepath(self):
        self.color = YELLOW

    def draw(self, w):
        pg.draw.rect(w, self.color, (self.x, self.y, self.wid, self.wid))

    def upneigh(self, grid):
        self.neighb = []

        # DOWN
        if self.row < self.tot_rows - 1 and not grid[self.row + 1][self.col].isobstacle():
            self.neighb.append(grid[self.row + 1][self.col])

        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].isobstacle():
            self.neighb.append(grid[self.row - 1][self.col])

        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].isobstacle():
            self.neighb.append(grid[self.row][self.col - 1])

        # RIGHT
        if self.col < self.tot_rows - 1 and not grid[self.row][self.col + 1].isobstacle():
            self.neighb.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False

# heuristic function
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# drawing the final path
def final_path(prev, i, start, draw):
    while i in prev:
        i = prev[i]
        if i != start:
            i.makepath()
        draw()

# A star algorithm
def astar(draw, mp, start, end):
    cnt = 0
    opset = []
    heapq.heapify(opset)
    heapq.heappush(opset, (0, cnt, start))
    prev = defaultdict(int) # storing the path

    gscore = defaultdict(float)
    for row in mp:
        for nd in row:
            gscore[nd] = float("inf")

    gscore[start] = 0

    fscore = defaultdict(float)
    for row in mp:
        for nd in row:
            fscore[nd] = float("inf")

    fscore[start] = h(start.getpos(), end.getpos())

    opset_hash = defaultdict(bool)

    while opset:
        # print(opset)
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                pg.quit()

        curr = opset[0][2]
        heapq.heappop(opset)
        opset_hash[curr] = True

        if curr == end:
            final_path(prev, end, start, draw)
            end.do_end()
            return True

        for i in curr.neighb:
            tempg = gscore[curr] + 1

            if tempg < gscore[i]:
                prev[i] = curr
                gscore[i] = tempg
                fscore[i] = tempg + h(i.getpos(), end.getpos())
                if not opset_hash[i]:
                    cnt += 1
                    heapq.heappush(opset, (fscore[i], cnt, i))
                    opset_hash[i] = True
                    i.open()
        draw()

        if curr != start:
            curr.block()

    return False

# creating the grid square
def makegrid(rows, wid):
    mp = [[] for i in range(rows)]
    gap = wid // rows
    for i in range(rows):
        for j in range(rows):
            nd = Node(i, j, gap, rows)
            mp[i].append(nd)

    return mp

# drawing grid lines
def drawlines(w, rows, wid):
    gap = wid // rows
    for i in range(rows):
        pg.draw.line(w, GREY, (0, i * gap), (wid, i * gap))
        for j in range(rows):
            pg.draw.line(w, GREY, (j * gap, 0), (j * gap, wid))

# drawing final grid
def draw(w, mp, rows, wid):
    w.fill(WHITE)

    for row in mp:
        for nd in row:
            nd.draw(w)
    drawlines(w, rows, wid)

    pg.display.update()

# Getting mouse's position
def getmouse_pos(pos, rows, wid):
    gap = wid // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

# Main
def main(w, wid):
    ROWS = 50
    mp = makegrid(ROWS, wid)

    start, end = None, None
    run, started = True, False

    # Mainloop
    while run:
        draw(w, mp, ROWS, wid)
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                run = False

            if started:
                continue

            # LMB to add spot
            if pg.mouse.get_pressed()[0]:
                pos = pg.mouse.get_pos()
                row, col = getmouse_pos(pos, ROWS, wid)
                nd = mp[row][col]
                if not start and nd != end:
                    start = nd
                    start.do_start()

                elif not end and nd != start:
                    end = nd
                    end.do_end()

                elif nd != start and nd != end:
                    nd.obstacle()

            # RMB to remove spot
            elif pg.mouse.get_pressed()[2]:
                pos = pg.mouse.get_pos()
                row, col = getmouse_pos(pos, ROWS, wid)
                nd = mp[row][col]
                nd.reset()
                if nd == start:
                    start = None
                elif nd == end:
                    end = None

            # Space to start simulation
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_SPACE and not started:
                    for row in mp:
                        for nd in row:
                            nd.upneigh(mp)

                    astar(lambda: draw(w, mp, ROWS, wid), mp, start, end)
    # Kill
    pg.quit()

main(WIN, sze)