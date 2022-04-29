import random as r
import math
import numpy as np
import tkinter as tk
import heapq
import itertools
import random

class Player:
    pol = []
    n = None

    def __init__(self,n, pol=[],score=0 ):
        self.n = n
        self.pol = pol
        self.score = 0

    def add_seg(self,s):
        self.pol.append(s)

class Point:
    x = 0.0
    y = 0.0

    def __init__(self, x, y, player = None):
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

    def __init__(self, p, player = None, a=None, b=None):
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

    def finish(self, p, edge = False):
        if not edge :
            if self.done: return
            self.end = p
            self.done = True
        else :
            self.end = p
            self.done = True

    def point(self,p1,p2):
        self.p1=p1
        self.p2=p2

    def hauteur(self,p):
        x0 = (self.p1.x + self.p2.x)/2
        y0 = (self.p1.y + self.p2.y)/2
        p_inter = Point(x0,y0)
        print(p.distance(p_inter))
        return p.distance(p_inter)

    def actu_score(self):
            if self.p1 != None and not self.score1:
                self.p1.player.score += self.hauteur(self.p1)*(self.start.distance(self.end))/2
                print(self.p1.player.score)
                self.score1 = True
            if self.p2 != None and not self.score1:
                self.p2.player.score += self.hauteur(self.p2)*(self.start.distance(self.end))/2
                print(self.p2.player.score)
                self.score2 = True

    def p_edge(self,p):
        if self.start.x - self.end.x != 0 :
            a = (self.end.y - self.start.y)/(self.end.x - self.start.x)
            x2 = 500
            y2 = a*(500 - self.start.x) + self.start.y
            if 0 < y2 < 500 and p.x > self.p1.x :
                return Point(x2,y2)

            x2 = 0
            y2 = a*(0 - self.start.x) + self.start.y
            if 0 < y2 < 500 and p.x < self.p1.x :
                return Point(x2,y2)

            y2 = 500
            x2 = (500)/a - self.start.y/a + self.start.x
            if 0 < x2 < 500 and p.y > self.p1.y :
                return Point(x2,y2)

            y2 = 0
            x2 = (-self.start.y)/a + self.start.x
            if 0 < x2 < 500 and p.y < self.p1.y :
                return Point(x2,y2)
        elif p.y > 500:
            return Point(p.x, 500)
        else :
            return Point(p.x, 0)

    def inter_edge(self): # si on considère la boite abcd où a est le coin inférieur gauche b le coin inférieur droit alors le bords 1 est ab, 2 bc, 3 cd et 4da

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
        if item in self.entry_finder: return
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



# Source: (C++) http://www.cs.hmc.edu/~mbrubeck/voronoi.html

class Voronoi:
    def __init__(self, points, player = Player(1), bot = Player(0)):
        self.player = Player(1)
        self.bot = Player(0)
        self.output = [] # liste des segments qui forment le diagramme de Voronoï
        self.arc = None  # arbre binaire pour les paraboles
        self.points = PriorityQueue() # événements ponctuels
        self.event = PriorityQueue() # événements circulaires

        # On pose la boîte dans laquelle on trace la diagramme (bounding box)
        self.x0 = -50.0
        self.x1 = -50.0
        self.y0 = 550.0
        self.y1 = 550.0

        # Insertion des points en tant qu'évènements ponctuels
        for pts in points:
            if pts[2] == 0 :
                point = Point(pts[0], pts[1], player = self.bot)
            else :
                point = Point(pts[0], pts[1], player = self.player)
            self.points.push(point)
            # On agrandit la boîte si nécessaire
            if point.x < self.x0: self.x0 = point.x
            if point.y < self.y0: self.y0 = point.y
            if point.x > self.x1: self.x1 = point.x
            if point.y > self.y1: self.y1 = point.y
        # add margins to the bounding box
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 = self.x0 - dx
        self.x1 = self.x1 + dx
        self.y0 = self.y0 - dy
        self.y1 = self.y1 + dy

    def process(self):
        while not self.points.empty():
            if not self.event.empty() and (self.event.top().x <= self.points.top().x):
                self.process_event() # handle circle event
            else:
                self.process_point() # handle site event

        # after all points, process remaining circle events
        while not self.event.empty():
            self.process_event()

        self.finish_edges()

    def process_point(self):
        # get next event from site pq
        p = self.points.pop()
        # add new arc (parabola)
        self.arc_insert(p)

    def process_event(self):
        # get next event from circle pq
        e = self.event.pop()
        #print("Process Event : x =", e.x)

        if e.valid:
            # start new edge
            s = Segment(e.p, p1 = e.p0, p2 = e.p1)
            self.output.append(s)
            #print("Add segment : S(", s.start,"-", s.end,")",'p12_segment',s.p1,s.p2)

            # remove associated arc (parabola)
            a = e.a
            if a.pprev is not None:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext is not None:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s

            # finish the edges before and after a
            if a.s0 is not None:
                a.s0.finish(e.p)
            if a.s1 is not None:
                a.s1.finish(e.p)
            # recheck circle events on either side of p
            if a.pprev is not None: self.check_circle_event(a.pprev, e.x)
            if a.pnext is not None: self.check_circle_event(a.pnext, e.x)

    def arc_insert(self, p): #beachline
        #print("Ajout d'une parabole pour p: x =", p.x,",y =", p.y)
        if self.arc is None:
            self.arc = Arc(p)
        else:
            # find the current arcs at p.y
            i = self.arc
            while i is not None:
                flag, z = self.intersect(p, i)
                if flag:
                    # new parabola intersects arc i
                    flag, zz = self.intersect(p, i.pnext)
                    if (i.pnext is not None) and (not flag):
                        i.pnext.pprev = Arc(i.p, player = i.p.player ,a = i, b = i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.p, player = i.p.player ,a = i)
                    i.pnext.s1 = i.s1

                    # add p between i and i.pnext
                    i.pnext.pprev = Arc(p, player = p.player, a = i, b = i.pnext)
                    i.pnext = i.pnext.pprev

                    i = i.pnext # now i points to the new arc

                    # add new half-edges connected to i's endpoints
                    seg = Segment(z, p1 = p, p2 = i.p)
                    self.output.append(seg)
                    i.pprev.s1 = i.s0 = seg

                    seg = Segment(z, p1 = p, p2 = i.pprev.p)
                    self.output.append(seg)
                    i.pnext.s0 = i.s1 = seg

                    # check for new circle events around the new arc
                    self.check_circle_event(i, p.x)
                    self.check_circle_event(i.pprev, p.x)
                    self.check_circle_event(i.pnext, p.x)

                    return

                i = i.pnext

            # if p never intersects an arc, append it to the list
            i = self.arc
            while i.pnext is not None:
                i = i.pnext
            i.pnext = Arc(p, player = p.player, a = i)

            # insert new segment between p and i
            x = self.x0
            y = (i.pnext.p.y + i.p.y) / 2.0;
            start = Point(x, y)

            seg = Segment(start, p1 = p, p2 = i.p)
            i.s1 = i.pnext.s0 = seg
            self.output.append(seg)

    def check_circle_event(self, i, x0):
        # look for a new circle event for arc i
        if (i.e is not None) and (i.e.x  != self.x0):
            i.e.valid = False
        i.e = None

        if (i.pprev is None) or (i.pnext is None): return

        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and (x > self.x0):
            i.e = Event(x, o, i, i.pprev.p, i.pnext.p)
            self.event.push(i.e)

    def circle(self, a, b, c):
        # check if bc is a "right turn" from ab
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))

        if (G == 0): return False, None, None # Points are co-linear

        # point o is the center of the circle
        ox = 1.0 * (D*E - B*F) / G
        oy = 1.0 * (A*F - C*E) / G

        # o.x plus radius equals max x coord
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        o = Point(ox, oy)

        return True, x, o

    def intersect(self, p, i):
        # check whether a new parabola at point p intersect with arc i
        if (i is None): return False, None
        if (i.p.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.pprev != None:
            a = (self.intersection(i.pprev.p, i.p, 1.0*p.x)).y
        if i.pnext != None:
            b = (self.intersection(i.p, i.pnext.p, 1.0*p.x)).y

        if (((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.p.x)**2 + (i.p.y-py)**2 - p.x**2) / (2*i.p.x - 2*p.x)
            res = Point(px, py)
            return True, res
        return False, None

    def intersection(self, p0, p1, l):
        # get the intersection of two parabolas
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == l):
            py = p1.y
        elif (p0.x == l):
            py = p0.y
            p = p1
        else:
            # use quadratic formula
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1.0/z0 - 1.0/z1;
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = 1.0 * (p0.y**2 + p0.x**2 - l**2) / z0 - 1.0 * (p1.y**2 + p1.x**2 - l**2) / z1

            py = 1.0 * (-b-math.sqrt(b*b - 4*a*c)) / (2*a)

        px = 1.0 * (p.x**2 + (p.y-py)**2 - l**2) / (2*p.x-2*l)
        res = Point(px, py)
        return res

    def clean_output(self):
        for s1 in self.output:
            if s1.end == None :
                self.output.remove(s1)
            for s2 in self.output:
                if s1 != s2 and [s1.start.x, s1.start.y, s1.end.x, s1.end.y] == [s2.start.x, s2.start.y, s2.end.x, s2.end.y]:
                    self.output.remove(s2)


    def finish_edges(self):
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.pnext != None:
            if i.s1 != None:
                p = self.intersection(i.p, i.pnext.p, l*2.0)
                i.s1.finish(p)
            i = i.pnext

        self.clean_output()
        for s in self.output :
            s.inter_edge()
            print(s.start.x)
            print(s.end.x)

        Ls_edge = self.correct_seg()
        self.output += Ls_edge

        self.clean_output()


    def next_edge(self,n,direction,s,s_edge): # fonction qui a un segment s ayant pour extremité s_edge sur le bord n du canvas trouve le segment ininterrompu qui longe c bord dans le direction : direction (=1 pour montée =0 pour descente en regardant le bord gauche)
        s_new = Segment(s_edge)
        corner = (False,Point(-1,-1))
        if n == 1:
            assert(s_edge.x == 500) # bord droit du canvas
            Ls =[]
            Ly = []
            for s2 in self.output:
                if direction == 1 : #montée
                    b2 = s2.start.y > s_edge.y
                else :
                    b2 = s2.start.y < s_edge.y #descente

                if s2.start.x == 500 and b2 : #si un segment interromp le longement du bord on le note
                    Ls.append((s2,'s'))
                    Ly.append(s2.start.y)

                if direction == 1 :
                    b2 = s2.end.y > s_edge.y
                else :
                    b2 = s2.end.y < s_edge.y

                if s2.end.x == 500 and b2 :
                    Ls.append((s2,'e'))
                    Ly.append(s2.end.y)

            if len(Ls) > 0 :
                if direction == 1 :
                    s0,str = Ls[Ly.index(min(Ly))]
                else :
                    s0,str = Ls[Ly.index(max(Ly))]
                if str == 's' :
                    s_new.finish(s0.start)
                else :
                    s_new.finish(s0.end)
            else :
                if direction == 1 :
                    s_new.finish(Point(500,500))
                    corner = (True,Point(500,500))
                else:
                    s_new.finish(Point(500,0))
                    corner = (True,Point(500,0))
            # s_new est donc le segment qui va de s_edge au premier point qui interromp le parcours du bord depuis s_edge dans la direction : direction

        if n == 2:
            assert(s_edge.y == 500) # bord haut du canvas
            Ls =[]
            Lx = []
            for s2 in self.output:
                if direction == 1 :
                    b2 = s2.start.x < s_edge.x
                else :
                    b2 = s2.start.x > s_edge.x

                if s2.start.y == 500 and b2 : #si un segment interromp le longement du bord on le note
                    Ls.append((s2,'s'))
                    Lx.append(s2.start.x)

                if direction == 1 :
                    b2 = s2.end.x < s_edge.x
                else :
                    b2 = s2.end.x > s_edge.x

                if s2.end.y == 500 and b2 :
                    Ls.append((s2,'e'))
                    Lx.append(s2.end.x)

            if len(Ls) > 0 :
                if direction == 1:
                    s0,str = Ls[Lx.index(max(Lx))]
                else:
                    s0,str = Ls[Lx.index(min(Lx))]
                if str == 's' :
                    s_new.finish(s0.start)
                else :
                    s_new.finish(s0.end)
            else :
                if direction == 1 :
                    s_new.finish(Point(0,500))
                    corner = (True,Point(0,500))
                else:
                    s_new.finish(Point(500,500))
                    corner = (True,Point(500,500))

        if n == 3:
            assert(s_edge.x == 0) # bord gauche du canvas
            Ls =[]
            Ly = []
            for s2 in self.output:
                if direction == 1 :
                    b2 = s2.start.y < s_edge.y
                else :
                    b2 = s2.start.y > s_edge.y

                if s2.start.x == 0 and b2 : #si un segment interromp le longement du bord on le note
                    Ls.append((s2,'s'))
                    Ly.append(s2.start.y)

                if direction == 1 :
                    b2 = s2.end.y < s_edge.y
                else :
                    b2 = s2.end.y > s_edge.y

                if s2.end.x == 0 and b2 :
                    Ls.append((s2,'e'))
                    Ly.append(s2.end.y)

            if len(Ls) > 0 :
                if direction == 1:
                    s0,str = Ls[Ly.index(max(Ly))]
                else:
                    s0,str = Ls[Ly.index(min(Ly))]
                if str == 's' :
                    s_new.finish(s0.start)
                else :
                    s_new.finish(s0.end)
            else :
                if direction == 1 :
                    s_new.finish(Point(0,0))
                    corner = (True,Point(0,0))
                else:
                    s_new.finish(Point(0,500))
                    corner = (True,Point(0,500))

        if n == 4:
            assert(s_edge.y == 0) # bord bas du canvas
            Ls =[]
            Lx = []
            for s2 in self.output:
                if direction == 1 :
                    b2 = s2.start.x > s_edge.x
                else :
                    b2 = s2.start.x < s_edge.x

                if s2.start.y == 0 and b2 : #si un segment interromp le longement du bord on le note
                    Ls.append((s2,'s'))
                    Lx.append(s2.start.x)

                if direction == 1 :
                    b2 = s2.end.x < s_edge.x
                else :
                    b2 = s2.end.x > s_edge.x

                if s2.end.y == 0 and b2 :
                    Ls.append((s2,'e'))
                    Lx.append(s2.end.x)

            if len(Ls) > 0 :
                if direction == 1:
                    s0,str = Ls[Lx.index(min(Lx))]
                else:
                    s0,str = Ls[Lx.index(max(Lx))]
                if str == 's' :
                    s_new.finish(s0.start)
                else :
                    s_new.finish(s0.end)
            else :
                if direction == 1 :
                    s_new.finish(Point(500,0))
                    corner = (True,Point(500,0))
                else:
                    s_new.finish(Point(0,0))
                    corner = (True,Point(0,0))
        x8 = s_new.end.x
        y8 = s_new.end.y
        p_center = Point(s_new.start.x/2 + s_new.end.x/2, s_new.start.y/2 + s_new.end.y/2)
        d1 = s.p1.distance(p_center)
        d2 = -1
        if s.p2 is not None :
            d2 = s.p2.distance(p_center)
        if d2 > 0 and d2 < d1 :
            s_new.p1 = s.p2
        else :
            s_new.p1 = s.p1

        return s_new,corner


    def correct_seg(self):

        Ls_edge = []

        for s in self.output:
            print(s.start.x)
            print(s.start.y)
            if s.start.x == 500 :
                s_new, b_corner = self.next_edge(1,0,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 1
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(1,1,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 1
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

            if s.start.y == 500 :
                print("hellosy5")
                s_new, b_corner = self.next_edge(2,0,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 2
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(2,1,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 2
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

            if s.start.x == 0 :
                s_new, b_corner = self.next_edge(3,0,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 3
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(3,1,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 3
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

            if s.start.y == 0 :
                s_new, b_corner = self.next_edge(4,0,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 4
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(4,1,s,s.start)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 4
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

        #on fait pareil avec les s.end

            if s.end.x == 500 :
                s_new, b_corner = self.next_edge(1,0,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 1
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(1,1,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 1
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

            if s.end.y == 500 :
                s_new, b_corner = self.next_edge(2,0,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 2
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(2,1,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 2
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

            if s.end.x == 0 :
                s_new, b_corner = self.next_edge(3,0,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 3
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(3,1,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 3
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

            if s.end.y == 0 :
                s_new, b_corner = self.next_edge(4,0,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 4
                dir = -1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,0,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1

                s_new, b_corner = self.next_edge(4,1,s,s.end)
                Ls_edge.append(s_new)
                bool, corner = b_corner
                k = 0
                n0 = 4
                dir = 1
                while bool and k < 4:
                    n0 += dir
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
                    s_new, b_corner = self.next_edge(n0,1,s,corner)
                    Ls_edge.append(s_new)
                    bool, corner = b_corner
                    k += 1
        return Ls_edge


    def print_output(self):
        it = 0
        for o in self.output:
            it = it + 1
            p0 = o.start
            p1 = o.end
            print (p0.x, p0.y, p1.x, p1.y)

        for s in self.finish_edges():
            s0 = s.start
            s1 = s.end
            res.append((s0.x, s0.y, s1.x, s1.y))

    def get_output(self):
        res = []
        for o in self.output:
            p0 = o.start
            p1 = o.end
            res.append((p0.x, p0.y, p1.x, p1.y))
        return res



colors=["blue","green","red","yellow","purple"]

###################################################################################
#-------------------------------PARTIE TKINTER------------------------------------#
###################################################################################
"""
Dans cette partie, nous avons implémenté le jeu de Voronoï. Dans notre projet,
chaque joueur possède 5 points à placer. Les stratégies que nous avons implémentées
sont les suivantes:

1) La stratégie gloutonne ou greedy: A chaque coup, le bot joue le coup qui
    maximise son score. Comme le nombre de coup possible est infini nous discrétisons
    la surface de jeu en une grille de 20x20 soit 400 coup possibles pour le bot.

2) La stratégie MCTS (Monte-Carlo-Tree-Search): Pour chacun des 400 coups possibles
    le bot simule les 400 réponses possibles du joueur et calcul le score moyen des
    réponses du joueur. Le coup choisi est alors celui pour lequel le score moyen
    du joueur est le plus bas

3) La stratégie DBC (Defensive Balanced Cells): Une stratégie qui ne prend pas
    en compte les coups du joueur mais joue selon un patterne fixe bien défini.
    La stratégie construit un diagramme dit "équilibré" ou "balanced".
    On dit qu'un diagramme est équilibré si toutes les cellules le sont. Une cellule
    est dite équilibré si il existe une droite qui passe par le germe/noyau qui
    coupe la cellule en 2 parties d'aires égales. Pour plus de détails sur cette notion
    consulter : https://helios2.mi.parisdescartes.fr/~bouzy/publications/bouzy-acg13.pdf
    page 7 """

class MainWindow:
    # Rayon des points affichés sur le tkinter
    RADIUS = 3

    #Variable qui permet de vérouiller la fenêtre tkinter pour tracer le diagramme
    LOCK_FLAG = False

    def __init__(self, master):



        self.master = master
        self.master.title("Voronoi")

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=500, height=500)
        self.w.config(background='white')
        self.w.bind('<Double-1>', self.onDoubleClick)
        self.w.pack()

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()

        self.btnCalculate = tk.Button(self.frmButton, text='Calculate', width=25, command=self.onClickCalculate)
        self.btnCalculate.pack(side=tk.LEFT)

        #Bouton de choix de la stratégie de l'ordinateur#
        self.btnGreedyBot = tk.Button(self.frmButton, text='Stratégie Gloutonne', width=25, command=self.GreedyBot)
        self.btnGreedyBot.pack(side=tk.LEFT)

        self.btnMCTSBot = tk.Button(self.frmButton, text='Stratégie MCTS', width=25, command=self.MCTSBot)
        self.btnMCTSBot.pack(side=tk.LEFT)

        self.btnDBCBot = tk.Button(self.frmButton, text='Stratégie DBC', width=25, command=self.DBCBot)
        self.btnDBCBot.pack(side=tk.LEFT)



        #Bouton de reset du jeu#
        self.btnClear = tk.Button(self.frmButton, text='Clear', width=25, command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)


        #Affichage des scores du joueurs et du bot#
        self.score_user = 0
        self.score_user_variable = tk.StringVar(self.master, f'Score Joueur: {self.score_user}')
        self.score_user_lbl = tk.Label(self.master, textvariable=self.score_user_variable)
        self.score_user_lbl.pack()

        self.score_bot = 0
        self.score_bot_variable = tk.StringVar(self.master, f'Score Bot: {self.score_bot}')
        self.score_bot_lbl = tk.Label(self.master, textvariable=self.score_bot_variable)
        self.score_bot_lbl.pack()


        #Variable de compteur de tour#
        self.count = 0

        #Variable de choix de stratégie#
        self.strategy = 0



    # Pour le choix des stratégies, le bouton de chaque stratégie affecte une
    # valeur à la variable strategy qui vient changer la fonction de placement
    # de point du bot utilisé dans onDoubleClick
    def GreedyBot(self):
        self.strategy = 1

    def MCTSBot(self):
        self.strategy = 2

    def DBCBot(self):
        self.strategy = 3


    #Définition du bouton Calculate#
    def onClickCalculate(self):
        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True

            pObj = self.w.find_all()
            points = []
            for p in pObj:
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS))

            vp = Voronoi(points)
            vp.process()
            lines = vp.get_output()
            self.drawLinesOnCanvas(lines)


    #Définition du bouton Clear : Clear reset le jeu#
    def onClickClear(self):
        self.LOCK_FLAG = False
        self.w.delete(tk.ALL)
        self.score_user = 0
        self.score_bot = 0
        self.score_user_variable.set(f'Score Joueur: {self.score_user}')
        self.score_bot_variable.set(f'Score Bot: {self.score_bot}')
        self.count = 0




    #Donne le diagramme de Voronoi associé au point placés sur la fênetre tkinter #
    def get_vp(self):
        pObj = self.w.find_all()
        points = []
        for p in pObj:
            if self.w.itemcget(p, "fill") == "red":
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS,1))
            if self.w.itemcget(p, "fill") == "blue" or self.w.itemcget(p, "fill") == "yellow":
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS,0))

        vp = Voronoi(points)
        vp.process()
        return vp




    #Placement du point aléatoirement #
    def pc_place(self,points):
        #points est la liste de points déjà sur le plan on ajoute juste le point que place le bot
        x=r.random()*500
        y=r.random()*500
        self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "blue")
        points.append((x,y,0))





    #Placement du point selon la stratégie Defensive balanced cell#

    def DBC_place(self,points):

        DBC_list=[(350,350),(150,350),(350,150),(150,150),(250,250)]
        #Cette liste contient les coordonnées d'un diagramme de Voronoï équilibré à 5 points

        i=self.count
        (x,y)=DBC_list[i]
        self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "blue")
        points.append((x,y,0))




    #Placement du point selon la stratégie gloutonne ou greedy#
    def greedy_place(self,points):

        xy = [(i,j) for i in np.linspace(5,495,20) for j in np.linspace(5,495,20)]
        #Discrétisation du plan en une grille 20x20

        #Initialisation du max
        self.w.create_oval(xy[0][0]-self.RADIUS, xy[0][1]-self.RADIUS, xy[0][0]+self.RADIUS, xy[0][1]+self.RADIUS, fill= "yellow", tags = 'train')
        vp=self.get_vp()
        maxi = vp.bot.score/(10**4)
        (x_play,y_play) = (0,0)
        self.w.delete("train")


        #Boucle de recherche du max
        for (x,y) in xy:
            self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "yellow", tags = 'train')
            vp = self.get_vp()
            if vp.bot.score/(10**4) > maxi:
                maxi = vp.bot.score/(10**4)
                (x_play,y_play) = (x,y)
            self.w.delete("train")
        self.w.create_oval(x_play-self.RADIUS, y_play-self.RADIUS, x_play+self.RADIUS, y_play+self.RADIUS, fill= "blue")
        points.append((x_play,y_play,0))

    def onDoubleClick(self, event):
        if not self.LOCK_FLAG:
            self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill= "red")

        self.LOCK_FLAG = True
        #On efface les lignes du diagramme précédent

        self.w.delete("lines")

        #Calcul du diagramme de Voronoi via les points placés sur la fenêtre de jeu
        pObj = self.w.find_all()
        points = []
        for p in pObj:
            if self.w.itemcget(p, "fill") == "red":
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS,1))
            elif self.w.itemcget(p, "fill") == "blue":
                coord = self.w.coords(p)
                points.append((coord[0]+self.RADIUS, coord[1]+self.RADIUS,0))


        #Selection de la stratégie du bot #
        if self.strategy ==0:
            self.pc_place(points)


        elif self.strategy ==1:
            self.greedy_place(points)


        elif self.strategy ==3:

            self.DBC_place(points)


        vp = Voronoi(points)
        vp.process()
        lines = vp.get_output()


        #Actualisation du score du joueur et du bot #

        self.score_user = vp.player.score/(10**4)
        self.score_bot = vp.bot.score/(10**4)

        self.score_user_variable.set(f'Score Joueur: {self.score_user}')
        self.score_bot_variable.set(f'Score Bot: {self.score_bot}')


        #Tracer du diagramme de Voronoï
        self.drawLinesOnCanvas(lines)

        #Incrémentation du compteur de tour
        self.count += 1

        self.LOCK_FLAG = False

    def drawLinesOnCanvas(self, lines):
        n=0
        colors = ["blue","red","green","black","yellow"]*100
        for l in lines:
            n += 1
            self.w.create_line(l[0], l[1], l[2], l[3], fill=colors[n], tags="lines")



def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()

