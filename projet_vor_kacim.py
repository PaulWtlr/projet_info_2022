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

    def __init__(self,n,score=0 ):
        self.n = n
        self.polygons = []
        self.score = 0

    def add_pol(self,pol):
        self.polygons.append(pol)

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
        if self.end.x - self.start.x == 0 :
            p_inter = Point(self.start.x, p.y)
        if self.end.y - self.start.y == 0 :
            p_inter = Point(p.x,self.start.y)
        elif self.end.x - self.start.x != 0  :
            a1 = (self.end.y - self.start.y) / (self.end.x - self.start.x)
            a2 =  -1/a1 #pente de la droite perpendiculaire à self passant par p
            x0 = (-a1*(self.start.x) + a2*(p.x) - (p.y) + (self.start.y))/(a2 - a1) # abscisse du point d'intersection des deux droites
            y0 = a2*(x0 - p.x) + p.y
            p_inter = Point(x0,y0)

        return p.distance(p_inter)


    def actu_score(self):
            if self.p1 != None and not self.score1:
                self.p1.player.score += self.hauteur(self.p1)*(self.start.distance(self.end))/2
                self.score1 = True
            if self.p2 != None and not self.score1:
                self.p2.player.score += self.hauteur(self.p2)*(self.start.distance(self.end))/2
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

    def inter_edge(self):
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
        self.points_save = []
        self.event = PriorityQueue() # événements circulaires

        # On pose la boîte dans laquelle on trace la diagramme (bounding box)
        self.x0 = 0.0
        self.x1 = 0.0
        self.y0 = 0.0
        self.y1 = 0.0

        # Insertion des points en tant qu'évènements ponctuels
        for pts in points:
            if pts[2] == 0 :
                point = Point(pts[0], pts[1], player = self.bot)
            else :
                point = Point(pts[0], pts[1], player = self.player)
            self.points_save.append(point)
            self.points.push(point)
            # On agrandit la boîte si nécessaire
            if point.x < self.x0: self.x0 = point.x
            if point.y < self.y0: self.y0 = point.y
            if point.x > self.x1: self.x1 = point.x
            if point.y > self.y1: self.y1 = point.y
        # on ajoute des marges de sécurité
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 = self.x0 - dx
        self.x1 = self.x1 + dx
        self.y0 = self.y0 - dy
        self.y1 = self.y1 + dy

    def upd_pol(self,points):
        for p in points:
            pol=[]
            for s in self.output:
                if s.p1 is not None and (s.p1 == p or s.p2 == p):
                    #point0 = (s.start.x, s.start.y)
                    #point1 = (s.end.x, s.end.y)
                    point0 = (int(s.start.x), int(s.start.y))
                    point1 = (int(s.end.x),int(s.end.y))
                    if point0 not in pol:
                        pol.append(point0)
                    if point1 not in pol:
                        pol.append(point1)
            if len(pol) > 0:
                p.player.add_pol(pol)
        sort(self.player.polygons)
        sort(self.bot.polygons)

    def act_score2(self):
        self.player.score = area(self.player.polygons)
        self.bot.score = area(self.bot.polygons)


    def process(self):
        while not self.points.empty():
            if not self.event.empty() and (self.event.top().x <= self.points.top().x):
                self.process_event() # gère les évènements circulaires
            else:
                self.process_point() # gère les évènements ponctuels

        # après avoir traité les points les évènements circulaires restant sont traités
        while not self.event.empty():
            self.process_event()

        self.finish_edges()

    def process_point(self):
        #on récupère l'évènement ponctuel de la file de priorité
        p = self.points.pop()
        # ajoute la nouvelle parabole au front parabolique
        self.arc_insert(p)

    def process_event(self):
        # on récupère l'évènement circulaire de la file de priorité
        e = self.event.pop()


        if e.valid:
            # début d'un nouveau segment
            s = Segment(e.p, p1 = e.p0, p2 = e.p1)
            self.output.append(s)

            # on enlève la parabole "engloutie"
            a = e.a
            if a.pprev is not None:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext is not None:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s

            # termine les segments qui atteignent le noeud
            if a.s0 is not None:
                a.s0.finish(e.p)
            if a.s1 is not None:
                a.s1.finish(e.p)
            # on regarde alors si cette intervention a permit la création d'autres évènements circulaires
            if a.pprev is not None: self.check_circle_event(a.pprev, e.x)
            if a.pnext is not None: self.check_circle_event(a.pnext, e.x)

    def arc_insert(self, p): #beachline
        #print("Ajout d'une parabole pour p: x =", p.x,",y =", p.y)
        if self.arc is None:
            self.arc = Arc(p)
        else:
            # trouve l'arc parabolique à actualiser
            i = self.arc
            while i is not None:
                flag, z = self.intersect(p, i)
                if flag:
                    # nouvelle parabole qui intersecte le front i
                    flag, zz = self.intersect(p, i.pnext)
                    if (i.pnext is not None) and (not flag):
                        i.pnext.pprev = Arc(i.p, player = i.p.player ,a = i, b = i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.p, player = i.p.player ,a = i)
                    i.pnext.s1 = i.s1

                    # ajout de p entre les paraboles i.p et i.pnext
                    i.pnext.pprev = Arc(p, player = p.player, a = i, b = i.pnext)
                    i.pnext = i.pnext.pprev

                    i = i.pnext # on actualise alors i

                    # on ajoute alors les segments qui sont formés comme vu dans la partie théorique
                    seg = Segment(z, p1 = p, p2 = i.p)
                    self.output.append(seg)
                    i.pprev.s1 = i.s0 = seg

                    seg = Segment(z, p1 = p, p2 = i.pprev.p)
                    self.output.append(seg)
                    i.pnext.s0 = i.s1 = seg

                    # on n'oublie pas de regarder si nous avons engendrer des évènements circulaires
                    self.check_circle_event(i, p.x)
                    self.check_circle_event(i.pprev, p.x)
                    self.check_circle_event(i.pnext, p.x)

                    return

                i = i.pnext

            # si p n'intersecte pas le front on l'ajoute à la liste
            i = self.arc
            while i.pnext is not None:
                i = i.pnext
            i.pnext = Arc(p, player = p.player, a = i)

            # on ajoute un nouveau segment entre p et et i
            x = self.x0
            y = (i.pnext.p.y + i.p.y) / 2.0;
            start = Point(x, y)

            seg = Segment(start, p1 = p, p2 = i.p)
            i.s1 = i.pnext.s0 = seg
            self.output.append(seg)

    def check_circle_event(self, i, x0):
        # regarde si un nouvel évènement circulaire va se produire sur le front i lorsque la droite de balayage va atteindre x0
        if (i.e is not None) and (i.e.x  != self.x0):
            i.e.valid = False
        i.e = None

        if (i.pprev is None) or (i.pnext is None): return

        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and (x > self.x0):
            i.e = Event(x, o, i, i.pprev.p, i.pnext.p)
            self.event.push(i.e)

    def circle(self, a, b, c):
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))

        if (G == 0): return False, None, None # Points alignés

        # point o au centre du cercle
        ox = 1.0 * (D*E - B*F) / G
        oy = 1.0 * (A*F - C*E) / G

        # o.x plus le rayon égale max x coord
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        o = Point(ox, oy)

        return True, x, o

    def intersect(self, p, i):
        # regarde si la parabole associé à p intersect l'arc i
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
        # donne l'intersection des paraboles associés à p0(l) et p1(l) où l est l'abscisse de la droite de balayage
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == l):
            py = p1.y
        elif (p0.x == l):
            py = p0.y
            p = p1
        else:
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
            if s1.end is None :
                self.output.remove(s1)

        for s1 in self.output:
            for s2 in self.output:
                if s1 != s2 and [s1.start.x, s1.start.y, s1.end.x, s1.end.y] == [s2.start.x, s2.start.y, s2.end.x, s2.end.y]:
                    self.output.remove(s2)

    def correct_belonging(self):
        self.clean_output()
        Ls_edge = self.correct_seg()


        for s in self.output:
            assert s not in Ls_edge, 's est traité comme un non bord'
            p_aux = Point(s.start.x/2 + s.end.x/2,s.start.y/2 + s.end.y/2)
            Lp = [ p for p in self.points_save]
            Ld = [ p_aux.distance(p) for p in self.points_save]


            i = Ld.index(min(Ld))
            p1 = Lp[i]
            Lp.remove(p1)
            Ld.remove(Ld[i])
            i2 = Ld.index(min(Ld))
            p2 = Lp[i2]


            s.p1 = p1
            s.p2 = p2



        for s in Ls_edge:
            p_aux = Point(s.start.x/2 + s.end.x/2,s.start.y/2 + s.end.y/2)

            Lp = [ p for p in self.points_save]
            Ld = [ p_aux.distance(p) for p in self.points_save]


            i = Ld.index(min(Ld))
            p1 = Lp[i]
            s.p1 = p1
            s.p2 = None

        return Ls_edge



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


        Ls_edge = self.correct_belonging()


        #print(len(Ls_edge))
        #for s in Ls_edge:
        #    print('start',(int(s.start.x), int(s.start.y)),'end', (int(s.end.x), int(s.end.y)))
        self.output += Ls_edge
        #for s in self.output:
        #    s.actu_score()

        self.upd_pol(self.points_save)

    def is_in_large(self,s1,s2):
        if s1.start.x == s1.end.x and s2.start.x == s2.end.x and s1.start.x == s2.start.x:
            if s1.start.y < s1.end.y :
                if (s1.start.y >= s2.start.y and s1.end.y <= s2.end.y) or (s1.start.y >= s2.end.y and s1.end.y <= s2.start.y):
                    return True
            if s1.start.y >= s1.end.y :
                if (s1.end.y >= s2.start.y and s1.start.y <= s2.end.y) or (s1.end.y >= s2.end.y and s1.start.y <= s2.start.y):
                    return True
        elif s1.start.y == s1.end.y and s2.start.y == s2.end.y and s1.start.y == s2.start.y:
            if s1.start.x <= s1.end.x :
                if (s1.start.x >= s2.start.x and s1.end.x <= s2.end.x) or (s1.start.x >= s2.end.x and s1.end.x <= s2.start.x):
                    return True
            if s1.start.x > s1.end.x :
                if (s1.end.x >= s2.start.x and s1.start.x <= s2.end.x) or (s1.end.x >= s2.end.x and s1.start.x <= s2.start.x):
                    return True
        else :
            return False

    def is_in(self,s1,s2):
        if s1.start.x == s1.end.x and s2.start.x == s2.end.x and s1.start.x == s2.start.x:
            if s1.start.y < s1.end.y :
                if (s1.start.y > s2.start.y and s1.end.y < s2.end.y) or (s1.start.y > s2.end.y and s1.end.y < s2.start.y):
                    return True
            if s1.start.y > s1.end.y :
                if (s1.end.y > s2.start.y and s1.start.y < s2.end.y) or (s1.end.y > s2.end.y and s1.start.y < s2.start.y):
                    return True
        elif s1.start.y == s1.end.y and s2.start.y == s2.end.y and s1.start.y == s2.start.y:
            if s1.start.x < s1.end.x :
                if (s1.start.x > s2.start.x and s1.end.x < s2.end.x) or (s1.start.x > s2.end.x and s1.end.x < s2.start.x):
                    return True
            if s1.start.x > s1.end.x :
                if (s1.end.x > s2.start.x and s1.start.x < s2.end.x) or (s1.end.x > s2.end.x and s1.start.x < s2.start.x):
                    return True
        else :
            return False

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

                if direction == 1 and s2.end != None:
                    b2 = s2.end.y > s_edge.y
                elif s2.end != None :
                    b2 = s2.end.y < s_edge.y

                if s2.end != None and s2.end.x == 500 and b2 :
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

                if direction == 1 and s2.end != None :
                    b2 = s2.end.x < s_edge.x
                elif s2.end != None :
                    b2 = s2.end.x > s_edge.x

                if s2.end != None and s2.end.y == 500 and b2 :
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

                if direction == 1 and s2.end != None :
                    b2 = s2.end.y < s_edge.y
                elif s2.end != None :
                    b2 = s2.end.y > s_edge.y

                if s2.end != None and s2.end.x == 0 and b2 :
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

                if direction == 1 and s2.end != None :
                    b2 = s2.end.x < s_edge.x
                else :
                    b2 = s2.end.x > s_edge.x

                if s2.end != None and s2.end.y == 0 and b2 :
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
        #x8 = s_new.end.x
        #y8 = s_new.end.y
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
                    n0 = n0 % 4
                    if n0 == 0 :
                        n0 = 4
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
        for s1 in Ls_edge:
            for s2 in Ls_edge:
                if s1 != s2 and [int(s1.start.x), int(s1.start.y), int(s1.end.x), int(s1.end.y)] == [int(s2.start.x), int(s2.start.y), int(s2.end.x), int(s2.end.y)]:
                    Ls_edge.remove(s2)
                elif s1 != s2 and [int(s1.start.x), int(s1.start.y), int(s1.end.x), int(s1.end.y)] == [int(s2.end.x), int(s2.end.y), int(s2.start.x), int(s2.start.y)]:
                    Ls_edge.remove(s2)
                elif [int(s2.start.x), int(s2.start.y)] == [int(s2.end.x), int(s2.end.y)]:
                    Ls_edge.remove(s2)
                elif s1 != s2 and self.is_in_large(s1,s2):
                    Ls_edge.remove(s2)

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


        #Bouton de choix de la stratégie de l'ordinateur#
        self.btnGreedyBot = tk.Button(self.frmButton, text='Stratégie Bonne Pioche', width=25, command=self.BonnePiocheBot)
        self.btnGreedyBot.pack(side=tk.LEFT)

        self.btnAntiGagnantBot = tk.Button(self.frmButton, text='Stratégie Anti Gagnant', width=25, command=self.AntiGagnantBot)
        self.btnAntiGagnantBot.pack(side=tk.LEFT)

        self.btnDBCBot = tk.Button(self.frmButton, text='Stratégie DBC', width=25, command=self.DBCBot)
        self.btnDBCBot.pack(side=tk.LEFT)

        self.btnrandomBot = tk.Button(self.frmButton, text='Placement aléatoire (Par défaut)', width=25, command=self.randomBot)
        self.btnrandomBot.pack(side=tk.LEFT)


        #Bouton de reset du jeu#
        self.btnClear = tk.Button(self.frmButton, text='Rejouer', width=25, command=self.onClickClear)
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
    def randomBot(self):
        self.strategy = 0

    def BonnePiocheBot(self):
        self.strategy = 1

    def AntiGagnantBot(self):
        self.strategy = 2

    def DBCBot(self):
        self.strategy = 3

    #Définition du bouton Clear : Clear reset le jeu#
    def onClickClear(self):
        self.LOCK_FLAG = False
        self.w.delete(tk.ALL)
        self.score_user = 0
        self.score_bot = 0
        self.score_user_variable.set(f'Score Joueur: {self.score_user}')
        self.score_bot_variable.set(f'Score Bot: {self.score_bot}')
        self.count = 0
        self.strategy = 0




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
        vp.act_score2()
        return vp




    #Placement du point aléatoirement #
    def random_place(self,points):
        #points est la liste de points déjà sur le plan on ajoute juste le point que place le bot
        x=r.random()*500
        y=r.random()*500
        self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "blue")
        points.append((x,y,0))





    #Placement du point selon la stratégie Defensive balanced cell#

    def DBC_place(self,points):
        #Cette liste contient les coordonnées d'un diagramme de Voronoï équilibré à 5 points
        DBC_list=[(400,400),(100,400),(400,100),(100,100),(250,250)]

        #Cette liste contient une version legerement modifié de la liste précédente pour être plus imprévisible
        play_list = [ (x + random.choice((-1, 1))*r.random()*25, y + random.choice((-1, 1))*r.random()*25) for (x,y) in DBC_list]


        i=self.count
        (x,y)=play_list[i]
        self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "blue")
        points.append((x,y,0))


    def AntiGagnant_place(self,points):
        if self.count == 0:
            self.w.create_oval(250-self.RADIUS, 250-self.RADIUS, 250+self.RADIUS, 250+self.RADIUS, fill= "blue")
            points.append((250,250,0))
        else:
            vp = self.get_vp()
            list_coords = vp.player.polygons
            list_aire = [polygon_area(coords) for coords in list_coords]
            i = list_aire.index(max(list_aire))
            centre_pol_i = (sum([p[0] for p in list_coords[i]])/len(list_coords[i]),sum([p[1] for p in list_coords[i]])/len(list_coords[i]))

            (x_play,y_play) = centre_pol_i
            self.w.create_oval(x_play-self.RADIUS, y_play-self.RADIUS, x_play+self.RADIUS, y_play+self.RADIUS, fill= "blue")
            points.append((x_play,y_play,0))


    #Placement du point selon la stratégie bonne pioche#

    def BonnePioche_place(self,points):

        xy = [(r.random()*500,r.random()*500) for i in range(20)]


        self.w.create_oval(xy[0][0]-self.RADIUS, xy[0][1]-self.RADIUS, xy[0][0]+self.RADIUS, xy[0][1]+self.RADIUS, fill= "yellow", tags = 'train')
        vp=self.get_vp()
        maxi = vp.bot.score
        (x_play,y_play) = (0,0)
        self.w.delete("train")


        #Boucle de recherche du max
        for (x,y) in xy:
            self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "yellow", tags = 'train')
            vp = self.get_vp()
            if vp.bot.score > maxi:
                maxi = vp.bot.score
                (x_play,y_play) = (x,y)
            self.w.delete("train")
        self.w.create_oval(x_play-self.RADIUS, y_play-self.RADIUS, x_play+self.RADIUS, y_play+self.RADIUS, fill= "blue")
        points.append((x_play,y_play,0))

    def onDoubleClick(self, event):

        if self.count == 5:
            self.check_winner()

        else:
            if not self.LOCK_FLAG:
                self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill= "red")

            self.LOCK_FLAG = True
            #On efface les lignes du diagramme précédent

            self.w.delete("lines")
            self.w.delete("poly")
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
                self.random_place(points)


            elif self.strategy ==1:
                self.BonnePioche_place(points)

            elif self.strategy ==2:

                self.AntiGagnant_place(points)


            elif self.strategy ==3:

                self.DBC_place(points)


            vp = Voronoi(points)
            vp.process()
            lines = vp.get_output()
            vp.act_score2()


            #Actualisation du score du joueur et du bot #

            self.score_user = vp.player.score/(vp.bot.score + vp.player.score+1)
            self.score_bot = vp.bot.score/(vp.bot.score + vp.player.score+1)

            self.score_user_variable.set(f'Score Joueur: {self.score_user}')
            self.score_bot_variable.set(f'Score Bot: {self.score_bot}')




            #Tracer du diagramme de Voronoï
            self.drawPolygonOnCanvas(vp)
            self.drawLinesOnCanvas(lines)


            #Incrémentation du compteur de tour
            self.count += 1

            self.LOCK_FLAG = False

            print(vp.player.polygons)
            print(vp.bot.polygons)
            print('-----------------------------')

            if self.count == 5:
                self.check_winner()

    def drawLinesOnCanvas(self, lines):
        #n=0
        #colors = ["blue","red","green","black","yellow"]*100
        for l in lines:
            #n += 1
            #self.w.create_line(l[0], l[1], l[2], l[3],width = 2, fill=colors[n], tags="lines")
            self.w.create_line(l[0], l[1], l[2], l[3],width = 2, tags="lines")

    def drawPolygonOnCanvas(self,vp):


        for single_pol in vp.player.polygons:
            pol_trace = list(itertools.chain(single_pol))
            self.w.create_polygon(pol_trace, fill = "red", stipple='gray50', tags = "poly")

        for single_pol in vp.bot.polygons:
            pol_trace = list(itertools.chain(single_pol))
            self.w.create_polygon(pol_trace, fill = "blue", stipple='gray50', tags = "poly")

    def check_winner(self):
        if self.score_user > self.score_bot:
            self.w.create_text(250, 300, text="Le joueur a gagné", fill="red", font=('Helvetica 15 bold'))
            self.w.pack()

        elif self.score_user < self.score_bot:
            self.w.create_text(250, 300, text="L'ordinateur a gagné'", fill="blue", font=('Helvetica 15 bold'))
            self.w.pack()

        else:
            self.w.create_text(250, 300, text="Egalité'", fill="black", font=('Helvetica 15 bold'))
            self.w.pack()





def polygon_area(coords):
    # get x and y in vectors
    x = [point[0] for point in coords]
    y = [point[1] for point in coords]
    # shift coordinates
    x_ = x - np.mean(x)
    y_ = y - np.mean(y)
    # calculate area
    correction = x_[-1] * y_[0] - y_[-1] * x_[0]
    main_area = np.dot(x_[:-1], y_[1:]) - np.dot(y_[:-1], x_[1:])
    return 0.5 * np.abs(main_area + correction)

def area(list_coords):
    return np.sum([polygon_area(coords) for coords in list_coords])



def sort(pol):
    for single_pol in pol:
        cent=(sum([p[0] for p in single_pol])/len(single_pol),sum([p[1] for p in single_pol])/len(single_pol))
        single_pol.sort(key=lambda p: math.atan2(p[1]-cent[1],p[0]-cent[0]))
    return pol




def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()

