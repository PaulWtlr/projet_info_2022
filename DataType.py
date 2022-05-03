import random as r
import math
import numpy as np
import tkinter as tk
import heapq
import itertools
import random

class Player:
    polygons = []
    n = None

    def __init__(self, n, score=0):
        self.n = n
        self.polygons = []
        self.score = 0

    def add_pol(self, pol):
        self.polygons.append(pol)


class Point:
    x = 0.0
    y = 0.0

    def __init__(self, x, y, player=None):
        self.x = x
        self.y = y
        self.player = player

    def distance(self, p):
        return math.sqrt((self.x-p.x)**2 + (self.y-p.y)**2)


class Event:
    x = 0.0
    p = None
    a = None
    valid = True

    def __init__(self, x, p, a, p0, p1):
        self.x = x
        self.p = p
        self.a = a
        self.p0 = p0
        self.p1 = p1
        self.valid = True


class Arc:
    p = None
    pprev = None
    pnext = None
    e = None
    s0 = None
    s1 = None

    def __init__(self, p, player=None, a=None, b=None):
        self.player = player
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None
# Arc(p) définit la parabole associé au point p


class Segment:
    start = None
    end = None
    done = False
    p1 = None
    p2 = None
    score1 = False
    score2 = False

    def __init__(self, p, p1=None, p2=None):
        self.start = p
        self.end = None
        self.done = False
        self.p1 = p1
        self.p2 = p2

    def finish(self, p, edge=False):
        if not edge:
            if self.done:
                return
            self.end = p
            self.done = True
        else:
            self.end = p
            self.done = True

    def point(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def hauteur(self, p):
        if self.end.x - self.start.x == 0:
            p_inter = Point(self.start.x, p.y)
        if self.end.y - self.start.y == 0:
            p_inter = Point(p.x, self.start.y)
        elif self.end.x - self.start.x != 0:
            a1 = (self.end.y - self.start.y) / (self.end.x - self.start.x)
            # pente d'une droite perpendiculaire à self
            a2 = -1/a1
            # abscisse du point d'intersection des deux droites
            x0 = (-a1*(self.start.x) + a2*(p.x) - (p.y) + (
                self.start.y))/(a2 - a1)
            y0 = a2*(x0 - p.x) + p.y
            p_inter = Point(x0, y0)

        return p.distance(p_inter)

    def actu_score(self):
        if self.p1 is not None and not self.score1:
            self.p1.player.score += self.hauteur(self.p1)*(
                self.start.distance(self.end))/2
            self.score1 = True
        if self.p2 is not None and not self.score1:
            self.p2.player.score += self.hauteur(self.p2)*(
                self.start.distance(self.end))/2
            self.score2 = True

    def p_edge(self, p):
        # renvoie l'intersection du Segment self avec le bord qui est dépassé par le segment
        if self.start.x - self.end.x != 0:
            a = (self.end.y - self.start.y)/(self.end.x - self.start.x)
            x2 = 500
            y2 = a*(500 - self.start.x) + self.start.y
            if 0 < y2 < 500 and p.x > self.p1.x:
                return Point(x2, y2)

            x2 = 0
            y2 = a*(0 - self.start.x) + self.start.y
            if 0 < y2 < 500 and p.x < self.p1.x:
                return Point(x2, y2)

            y2 = 500
            x2 = (500)/a - self.start.y/a + self.start.x
            if 0 < x2 < 500 and p.y > self.p1.y:
                return Point(x2, y2)

            y2 = 0
            x2 = (-self.start.y)/a + self.start.x
            if 0 < x2 < 500 and p.y < self.p1.y:
                return Point(x2, y2)
        elif p.y > 500:
            return Point(p.x, 500)
        else:
            return Point(p.x, 0)

    def inter_edge(self):
        # regarde si un Segment dépasse un bord, si oui remet son extrémité sur le bord du canvas
        if self.start.x < 0 or self.start.x > 500 or self.start.y < 0 or self.start.y > 500:
            self.start = self.p_edge(self.start)

        if self.end.x < 0 or self.end.x > 500 or self.end.y < 0 or self.end.y > 500:
            self.end = self.p_edge(self.end)


class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        # check for duplicate
        if item in self.entry_finder:
            return
        count = next(self.counter)
        # use x-coordinate as a primary key (heapq in python is min-heap)
        entry = [item.x, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.pq
