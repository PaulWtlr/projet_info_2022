##DataType

import heapq
import itertools

import random as r


# définir une fonction distance ; à partir de cette fonction on peut calculer le score de chaque joueur dès lors qu'on a la liste des segments associées à chaque joueur
class Player:
    pol = []
    n = None

    def __init__(self,n, pol=[],score=0 ):
        self.n = n
        self.pol = pol
        self.score = 0

    def ajoute_seg(self,s):
        self.pol.append(s)

class Point:
    x = 0.0
    y = 0.0

    def __init__(self, x, y, player = None):
        self.x = x
        self.y = y
        self.player = player

    def distance(self, p):
        return math.sqrt((self.x-p.x)**2+(self.y-p.y)**2)

# Point(x,y) permet la création d'un point ayant pour coordonnées (x,y)


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
# Event(x,p,a) permet la création d'un évènement initialement vrai


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
    p1 = None
    p2 = None
    start = None
    end = None
    done = False
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

        return p.distance(p_inter)

    def actu_score(self):
            if self.p1 != None and not self.score1:
                self.p1.player.score += self.hauteur(self.p1)*(self.start.distance(self.end))/2
                self.score1 = True
            if self.p2 != None and not self.score1:
                self.p2.player.score += self.hauteur(self.p2)*(self.start.distance(self.end))/2
                self.score2 = True
            
    
    def inter_edge(self,p): # si on considère la boite abcd où a est le coin inférieur gauche b le coin inférieur droit alors le bords 1 est ab, 2 bc, 3 cd et 4da
        if self.start.x - self.end.x != 0 :
            x2 = 500
            a = (self.end.y - self.start.y)/(self.end.x - self.start.x)
            y2 = a*(500 - self.start.x) + self.start.y 
            if 0 < y2 < 500 and p.x > self.p1.x :
                return Point(x2,y2)
            
            x2 = 0
            a = (self.end.y - self.start.y)/(self.end.x - self.start.x)
            y2 = -a*(self.start.x) + self.start.y 
            if 0 < y2 < 500 and p.x < self.p1.x :
                return Point(x2,y2)
            
            y2 = 500
            a = (self.end.y - self.start.y)/(self.end.x - self.start.x)
            x2 = 500 / a - self.start.y/a + self.start.x
            if 0 < x2 < 500 and p.y > self.p1.y :
                return Point(x2,y2)
                    
            y2 = 0
            a = (self.end.y - self.start.y)/(self.end.x - self.start.x)
            x2 = - self.start.y/a + self.start.x
            if 0 < x2 < 500 and p.y < self.p1.y :
                return Point(x2,y2)
        elif p.y > 500:
            return Point(p.x, 500)
        else :
            return Point(p.x, 0)
# Segment définit un segment [a,b] en 2 temps :
# On commence par poser le point a :
#   s=Segment(a)
# Le segment est alors inachevé ie self.done=False
# On pose alors le point b :
#   s.finish(b)
# On obtient le segment [a,b] achevé ie self.done=True


# Ainsi lorsqu'on effectue actu_score sur la liste des segments à la fin de l'algorithme on a le score de chaque joueur qui est calculé, pour cela on a simplement besoin de  :
# avoir bien définit à quelle point est lié chaque segment et à quel joueur est lié chaque point


class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        if item in self.entry_finder: return # Si item est déjà dans la file on ne fait rien
        count = next(self.counter)
        entry = [item.x, count, item] # On utilise x en temps que clé primaire (raisonnable dans le cadre du problème)
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
        raise KeyError('pop réalisé sur une file vide')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top réalisé sur une file vide')

    def empty(self):
        return not self.pq
# On réalise ici une file de priorité à l'aide du module python prévu à cet effet heapq
# https://docs.python.org/3/library/heapq.html (pour plus d'informations sur ce module)


##Voronoi


import random
import math


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


        # On ajoute une marge de sécurité à la boîte
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 = self.x0 - dx
        self.x1 = self.x1 + dx
        self.y0 = self.y0 - dy
        self.y1 = self.y1 + dy

        #print("Dimensions de la boîte : x0 =",self.x0,"y0 =", self.y0,"x1 =",self.x1,"y1 =", self.y1 )

    def process(self):
        while not self.points.empty():
            if not self.event.empty() and (self.event.top().x <= self.points.top().x):
                self.process_event() # traite un évènement circulaire
            else:
                self.process_point() # traite un évènement ponctuel

        # une fois tous les évènements circulaires traités, les évènements ponctuels restant sont traités
        while not self.event.empty():
            self.process_event()

        self.finish_edges()

    def process_point(self):
        # get next event from site pq
        p = self.points.pop()
        #print("Process Point : x =", p.x,",y =", p.y)
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
                a.s0.actu_score()
            if a.s1 is not None:
                a.s1.finish(e.p)
                a.s1.actu_score()
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
                        i.pnext = Arc(i.p, i)
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
            i.pnext = Arc(p, i)

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

        if i.pprev is not None:
            a = (self.intersection(i.pprev.p, i.p, 1.0*p.x)).y
        if i.pnext is not None:
            b = (self.intersection(i.p, i.pnext.p, 1.0*p.x)).y

        if (((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.p.x)**2 + (i.p.y-py)**2 - p.x**2) / (2*i.p.x - 2*p.x)
            res = Point(px, py)
            #print("Intersect point p(", p.x,",", p.y, ") and arc(", i.p.x,",", i.p.y, ") on point I(", px,",",py,")")
            return True, res
        #print("No intersect")
        return False, None

    def intersection(self, p0, p1, l):
        # fournit l'intersection de 2 paraboles
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
            for s2 in self.output:
                if s1 != s2 and [s1.start.x, s1.start.y, s1.end.x, s1.end.y] == [s2.start.x, s2.start.y, s2.end.x, s2.end.y]:
                    self.output.remove()

    def finish_edges(self):
        
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.pnext is not None:
            if i.s1 is not None:
                p = self.intersection(i.p, i.pnext.p, l*2.0)
                i.s1.finish(p)
                p_bord = i.s1.inter_edge(p)
                i.s1.finish(p_bord, edge = True)
                i.s1.actu_score()
            i = i.pnext
        
        s_edge=[]
        
        def next_edge(x,y,p1,p2):
            for s1 in self.output:
                if x == 0 or x == 500 :
                    if s1.start.x == x and s1.start.y > y :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                            
                    elif s1.done and s1.end.x == x and s1.end.y > y :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                            
                    else :
                        if s1.p1.y > s1.p2.y :
                            s = Segment(Point(x,y), p1 = s1.p1)
                        else :
                            s = Segment(Point(x,y), p1 = s1.p2)
                        s.finish(Point(x,500))
                        s_edge.append(s)
                    
                    
                    if s1.start.x == x and s1.start.y < y :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.start.y))
                            s_edge.append(s)
                            
                    elif s1.done and s1.end.x == x and s1.end.y < y :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(x,s1.end.y))
                            s_edge.append(s)
                    else :
                        if s1.p1.y < s1.p2.y :
                            s = Segment(Point(x,y), p1 = s1.p1)
                        else :
                            s = Segment(Point(x,y), p1 = s1.p2)
                        s.finish(Point(x,0))
                        s_edge.append(s)
                    
                elif y == 0 or y == 500 :
                     
                    if s1.start.y == y and s1.start.x > x :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                            
                    if s1.done and s1.end.y == y and s1.end.x > x :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                            
                    else :
                        if s1.p1.x < s1.p2.x :
                            s = Segment(Point(x,y), p1 = s1.p1)
                        else :
                            s = Segment(Point(x,y), p1 = s1.p2)
                        s.finish(Point(500,y))
                        s_edge.append(s)
                    
                    
                    if s1.start.y == y and s1.start.x < x :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.start.x,y))
                            s_edge.append(s)
                            
                    if s1.done and s1.end.y == y and s1.end.x < x :
                        p = p1
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                        p = p2
                        if s1.p1 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                        elif s1.p2 == p :
                            s = Segment(Point(x,y), p1 = p)
                            s.finish(Point(s1.end.x,y))
                            s_edge.append(s)
                            
                    else :
                        if s1.p1.x < s1.p2.x :
                            s = Segment(Point(x,y), p1 = s1.p1)
                        else :
                            s = Segment(Point(x,y), p1 = s1.p2)
                        s.finish(Point(0,y))
                        s_edge.append(s)
        
        for s1 in self.output:
            print(s1.start.x)
            print(s1.end.x)
            if (s1.start.x or s1.start.y) in {500,0}:
                print("hello")
                next_edge(s1.start.x,s1.start.y,s1.p1,s1.p2)
                n = 0
                while ((s_edge[-1].start.x,s_edge[-1].start.y) or (s_edge[-1].end.x,s_edge[-1].end.y)) in [(0,0),(0,500),(500,0),(500,500)] and n <= 4:
                     next_edge(s_edge[-1].start.x,s_edge[-1].start.y,s_edge[-1].p1,s_edge[-1].p2)
                     n += 1
        print(len(s_edge))
        for s in s_edge :
            s.actu_score
        return s_edge
        
    def print_output(self):
        it = 0
        for o in self.output:
            it = it + 1
            p0 = o.start
            p1 = o.end
            print (p0.x, p0.y, p1.x, p1.y)

    def get_output(self):
        res = []
        for o in self.output:
            p0 = o.start
            p1 = o.end
            res.append((p0.x, p0.y, p1.x, p1.y))
        for s in self.finish_edges():
            s0 = s.start
            s1 = s.end
            res.append((s0.x, s0.y, s1.x, s1.y))
        print('SCORE DU JOUEUR:',int(self.player.score/(10**2)),'SCORE DU BOT:',int(self.bot.score/(10**2)))
        
        return res


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




import tkinter as tk
import numpy as np

#  je veux une liste de int pour indiquer quel joueur joue quel point

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

            print (lines)

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
        print(pObj)
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
        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3], fill='black', tags="lines")



def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()

