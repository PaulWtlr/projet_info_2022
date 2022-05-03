import random as r
import math
import numpy as np
import tkinter as tk
import heapq
import itertools
import random

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
            assert(s_edge.x == 500) # bord gauche du canvas
            Ls =[]
            Ly = []
            for s2 in self.output:
                if direction == 1 :
                    b2 = s2.start.y > s_edge.y
                else :
                    b2 = s2.start.y < s_edge.y

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
            assert(s_edge.y == 500)
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
            assert(s_edge.x == 0)
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
            assert(s_edge.y == 0)
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


