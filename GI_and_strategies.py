import random as r
import math
import numpy as np
import tkinter as tk
import heapq
import itertools
import random
import DataType
import VoronoiGame
###################################################################################
#-------------------------------PARTIE TKINTER------------------------------------#
###################################################################################


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

        #Bouton de choix du mode jeu
        self.btn2users = tk.Button(self.frmButton, text='Mode de jeu 2 joueurs', width=25, command=self.mode_2_users)
        self.btn2users.pack(side=tk.RIGHT)

        #Bouton de choix de la stratégie de l'ordinateur#
        self.btnGreedyBot = tk.Button(self.frmButton, text='Stratégie Bonne Pioche', width=25, command=self.BonnePiocheBot)
        self.btnGreedyBot.pack(side=tk.RIGHT)

        self.btnAntiGagnantBot = tk.Button(self.frmButton, text='Stratégie Anti Gagnant', width=25, command=self.AntiGagnantBot)
        self.btnAntiGagnantBot.pack(side=tk.RIGHT)

        self.btnDBCBot = tk.Button(self.frmButton, text='Stratégie DBC', width=25, command=self.DBCBot)
        self.btnDBCBot.pack(side=tk.RIGHT)

        self.btnrandomBot = tk.Button(self.frmButton, text='Placement aléatoire (Par défaut)', width=25, command=self.randomBot)
        self.btnrandomBot.pack(side=tk.RIGHT)


        #Bouton de reset du jeu#
        self.btnClear = tk.Button(self.frmButton, text='Rejouer', width=25, command=self.onClickClear)
        self.btnClear.pack(side=tk.RIGHT)


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


        #Variable mode de jeu 1 ou 2 joueurs
        self.game_mode = 0



    def mode_2_users(self):
        self.game_mode = 1
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
        self.game_mode = 0




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
    def random_place(self):
        #points est la liste de points déjà sur le plan on ajoute juste le point que place le bot
        x=r.random()*500
        y=r.random()*500
        self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "blue")





    #Placement du point selon la stratégie Defensive balanced cell#

    def DBC_place(self):
        #Cette liste contient les coordonnées d'un diagramme de Voronoï équilibré à 5 points
        DBC_list=[(400,400),(100,400),(400,100),(100,100),(250,250)]

        #Cette liste contient une version legerement modifié de la liste précédente pour être plus imprévisible
        play_list = [ (x + random.choice((-1, 1))*r.random()*25, y + random.choice((-1, 1))*r.random()*25) for (x,y) in DBC_list]


        i=self.count
        (x,y)=play_list[i]
        self.w.create_oval(x-self.RADIUS, y-self.RADIUS, x+self.RADIUS, y+self.RADIUS, fill= "blue")


    def AntiGagnant_place(self):
        if self.count == 0:
            self.w.create_oval(250-self.RADIUS, 250-self.RADIUS, 250+self.RADIUS, 250+self.RADIUS, fill= "blue")
        else:
            vp = self.get_vp()
            list_coords = vp.player.polygons
            list_aire = [polygon_area(coords) for coords in list_coords]
            i = list_aire.index(max(list_aire))
            centre_pol_i = (sum([p[0] for p in list_coords[i]])/len(list_coords[i]),sum([p[1] for p in list_coords[i]])/len(list_coords[i]))

            (x_play,y_play) = centre_pol_i
            self.w.create_oval(x_play-self.RADIUS, y_play-self.RADIUS, x_play+self.RADIUS, y_play+self.RADIUS, fill= "blue")


    #Placement du point selon la stratégie bonne pioche#

    def BonnePioche_place(self):

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

    def onDoubleClick(self, event):

        #On vérifie d'abord le mode de jeu

        #Mode de jeu solo
        if self.game_mode == 0:

            #On vérifie si le jeu doit s'arreter
            if self.count == 5:
                self.check_winner()

            else:
                if not self.LOCK_FLAG:
                    self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill= "red")

                self.LOCK_FLAG = True
                #On efface les lignes du diagramme précédent

                self.w.delete("lines")
                self.w.delete("poly")

                #Selection de la stratégie du bot #
                if self.strategy ==0:
                    self.random_place()

                elif self.strategy ==1:
                    self.BonnePioche_place()

                elif self.strategy ==2:
                    self.AntiGagnant_place()

                elif self.strategy ==3:
                    self.DBC_place()

                #On calcule le diagramme de Voronoi
                vp = self.get_vp()
                lines = vp.get_output()



                #Actualisation du score du joueur et du bot #

                self.score_user = int(1000*vp.player.score/(vp.bot.score + vp.player.score+1))/10
                self.score_bot = int(1000*vp.bot.score/(vp.bot.score + vp.player.score+1))/10

                self.score_user_variable.set(f'Score Joueur: {self.score_user}%')
                self.score_bot_variable.set(f'Score Bot: {self.score_bot}%')

                #Tracer du diagramme de Voronoï
                self.drawPolygonOnCanvas(vp)
                self.drawLinesOnCanvas(lines)


                #Incrémentation du compteur de tour
                self.count += 1

                self.LOCK_FLAG = False

                if self.count == 5:
                    self.check_winner()


        #Mode de jeu 2 joueurs
        else:

            if self.count == 10:
                self.check_winner()

            #On décide de la couleur du point en fonction du tour
            if self.count%2 == 0 and not self.LOCK_FLAG:
                self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill= "red")

            if self.count%2 == 1 and not self.LOCK_FLAG:
                self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill= "blue")

            self.LOCK_FLAG = True

            #On efface les lignes du diagramme précédent

            self.w.delete("lines")
            self.w.delete("poly")

            #On calcule le diagramme de Voronoi
            vp = self.get_vp()
            lines = vp.get_output()

            #Actualisation du score des joueurs
            self.score_user = int(1000*vp.player.score/(vp.bot.score + vp.player.score+1))/10
            self.score_bot = int(1000*vp.bot.score/(vp.bot.score + vp.player.score+1))/10

            self.score_user_variable.set(f'Score Joueur 1: {self.score_user}%')
            self.score_bot_variable.set(f'Score Joueur 2: {self.score_bot}%')


            #Tracer du diagramme de Voronoï
            self.drawPolygonOnCanvas(vp)
            self.drawLinesOnCanvas(lines)


            #Incrémentation du compteur de tour
            self.count += 1

            self.LOCK_FLAG = False

            if self.count == 10:
                self.check_winner()




    def drawLinesOnCanvas(self, lines):

        for l in lines:
            self.w.create_line(l[0], l[1], l[2], l[3],width = 2, tags="lines")

    def drawPolygonOnCanvas(self,vp):


        for single_pol in vp.player.polygons:
            pol_trace = list(itertools.chain(single_pol))
            self.w.create_polygon(pol_trace, fill = "red", stipple='gray50', tags = "poly")

        for single_pol in vp.bot.polygons:
            pol_trace = list(itertools.chain(single_pol))
            self.w.create_polygon(pol_trace, fill = "blue", stipple='gray50', tags = "poly")



    def check_winner(self):

        if self.game_mode == 0:
            if self.score_user > self.score_bot:
                self.w.create_text(250, 300, text="Le joueur a gagné", fill="red", font=('Helvetica 15 bold'))
                self.w.pack()

            elif self.score_user < self.score_bot:
                self.w.create_text(250, 300, text="L'ordinateur a gagné'", fill="blue", font=('Helvetica 15 bold'))
                self.w.pack()

            else:
                self.w.create_text(250, 300, text="Egalité'", fill="black", font=('Helvetica 15 bold'))
                self.w.pack()


        #Si on a deux joueurs le texte affiché en fin de partie doit changer
        if self.game_mode == 1:
            if self.score_user > self.score_bot:
                self.w.create_text(250, 300, text="Le Joueur rouge a gagné", fill="red", font=('Helvetica 15 bold'))
                self.w.pack()

            elif self.score_user < self.score_bot:
                self.w.create_text(250, 300, text="Le Joueur bleu a gagné", fill="blue", font=('Helvetica 15 bold'))
                self.w.pack()

            else:
                self.w.create_text(250, 300, text="Egalité'", fill="black", font=('Helvetica 15 bold'))
                self.w.pack()





def polygon_area(coords):
    # On récupère les coordonnées x,y des sommets
    x = [point[0] for point in coords]
    y = [point[1] for point in coords]
    # On les décale par rapport au centre du polygone
    x_ = x - np.mean(x)
    y_ = y - np.mean(y)
    # On calcul l'aire via la formule du papillon
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