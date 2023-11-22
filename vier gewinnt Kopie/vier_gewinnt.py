from tkinter import*
from functools import partial
from random import randint
import time

############################################
##############Funktionalität################
############################################


# Variable speichert aktuellen Spieler. 1=rot, 2=gelb
spieler=1

# tauscht Spieler, der an der Reihe ist und gibt aktuellen Spieler auf Gewinnanzeige aus
def spielerwechsel():
    global spieler
    if spieler==1:
        spieler=2
        Gewinnanzeige.config(text="Gelb am Zug")
    else:
        spieler=1
        Gewinnanzeige.config(text="Rot am Zug")

# tauscht 1 für 2, bzw 2 für 1
# benötigt, wenn ki spielerwechsel simulieren will
def sim_spielerwechsel(x):
    if x==1:
        return 2
    else:
        return 1


# "spielfeld_lst" speichert virtuell den Spielstand in einer Liste.
# 0=unbesetzt, 1=rot, 2=gelb
spielfeld_lst=[]

# setzt spielfeld_lst auf Ausgangsposition
# Liste mit 7 listen, die jeweils eine Spalte repräsentieren
# in den Spaltenlisten jeweils 6 Listenelemente für jede Zeile
# die Elemente können folgende Werte annehmen
# 0=leer, 1=rot, 2=gelb (entsprechend den Spielernamen)
def resetspielfeld():
    global spielfeld_lst
    spielfeld_lst=[]
    for zeile in range (7):
        spalten_lst=[]
        for spalte in range (6):
            spalten_lst.append(0)
        spielfeld_lst.append(spalten_lst)

# zu Anfang wird spielfeld_lst auf Ausgangsposition gesetzt
resetspielfeld()            



# Funktion, die bei Knopfdruck aufgerufen wird
def spielzug(spalte):
    global spieler
    global spielfeld_lst
    global punkte_list

    # zeile entspricht der y-Koordinate
    # x-Koordinate bereits bekannt (ausgewählte Spalte)
    zeile=zeilefinden(spielfeld_lst,spalte)
    
    # wenn die ausgewählte Spalte voll ist, wird Spielzug abgebrochen und wiederholt
    if zeile==-1:
        return

    # Das Feld mit den ermittelten Koordinaten wird mit aktueller Spielfarbe besetzt
    # in virtuellem und visuellem Spielfeld
    spielfeld_lst[spalte][zeile]=spieler
    punkte_list[spalte][zeile].besetzen()

    # bei Sieg wird Funktion "gewonnen()" aufgerufen und Spielzug beendet
    if gewinnprüfung(spielfeld_lst,spalte,zeile):
        gewonnen()
        return

    
    # Spieler wird nur gewechselt, wenn noch nicht gewonnen wurde.
    spielerwechsel()

    # wenn Spielweise "gegen Computer" ausgewählt wurde, beginnt Spielzug der KI
    if spielweise.get()==2:
        KI_spielzug()


# sucht in ausgewählter Spalte erstes unbesetztes Feld von unten
# gibt Kommentar, wenn gewählte Spalte bereits voll ist
def zeilefinden(liste,spalte):
    zeile=5
    while True:
        if zeile == -1:
            Gewinnanzeige.config(text="Bitte andere Spalte wählen")
            return -1
        if liste[spalte][zeile]==0:
            return zeile
        zeile -= 1


        
# sucht nach vier in einer Reihe
def gewinnprüfung(liste,spalte,zeile):
   
    # suche in Zeile des geworfenen Steins nach vier in einer Reihe
    for i in range(4):
        if (not liste[i][zeile]==0) and \
        liste[i][zeile]==liste[i+1][zeile] and \
        liste[i][zeile]==liste[i+2][zeile] and \
        liste[i][zeile]==liste[i+3][zeile]:
            return True
    
    # Spalte
    for i in range(3):
        if (not liste[spalte][i]==0) and \
        liste[spalte][i]==liste[spalte][i+1] and \
        liste[spalte][i]==liste[spalte][i+2] and \
        liste[spalte][i]==liste[spalte][i+3]:
            return True

    # Diagonalen von rechts oben nach links unten
    # die Funktion such Orientierungsfeld an Spielfeldrand
    if spalte>zeile:
        x = spalte-zeile
        y = 0
    else:
        x = 0
        y = zeile-spalte

    # z beschreibt die Anzahl möglicher Gewinnkombinationen in einer Diagonale
    # abhängig von dem Orientierungsfeld
    z=0
    
    if x<2 and y==0:
        z=3
    elif x==2 or y==1:
        z=2
    elif x==3 or y==2:
        z=1

    # Schleife sucht z-mal nach 4 in einer Diagonalen
    for i in range(z):
            if (not liste[x+i][y+i]==0) and \
            liste[x+i][y+i]==liste[x+i+1][y+i+1] and \
            liste[x+i][y+i]==liste[x+i+2][y+i+2] and \
            liste[x+i][y+i]==liste[x+i+3][y+i+3]:
                return True
            
    # Diagonalen von rechts unten nach links oben
    # nach dem gleichen Schema
    if spalte>(5-zeile):
        x=spalte-(5-zeile)
        y=5
    else:
        x = 0
        y = zeile+spalte

    z = 0

    if x<2 and y==5:
        z=3
    elif x==2 or y==4:
        z=2
    elif x==3 or y==3:
        z=1 

    for i in range(z):
            if (not liste[x+i][y-i]==0) and \
            liste[x+i][y-i]==liste[x+i+1][(y-i)-1] and \
            liste[x+i][y-i]==liste[x+i+2][(y-i)-2] and \
            liste[x+i][y-i]==liste[x+i+3][(y-i)-3]:
                return True



# wird aufgerufen bei Sieg
# Knöpfe deaktiviert
# Gewinnanzeige geupdated
def gewonnen():
    global spieler
    global knöpfe_list

    for knopf in knöpfe_list:
        knopf.disable()
   
    if spieler==1:
        Gewinnanzeige.config(text="Rot hat gewonnen!")
    else:
        Gewinnanzeige.config(text="Gelb hat gewonnen!")



    
# setzt spieler, spielfeld_lst und GUI zurück
def neustart():
    global spieler
    global punkte_list
    global knöpfe_list

    if spieler==2:
        spielerwechsel()
    
    resetspielfeld()
    
    for spalte in range(7):
        for zeile in range(6):
            punkte_list[spalte][zeile].leeren()

    for knopf in knöpfe_list:
        knopf.enable()
            
    



##################################
############## Comp_Gegner ################
##################################

# Spielzug des Computers
# analog zu menschlichem Spielzug
def KI_spielzug():
    global spielfeld_lst
    global punkte_list
    global spieler

    # Variable "zug" beschreibt die auszuwählende Spalte
    zug = 0

    # Ki kopiert aktuelles Spielfeld, auf dem es modellieren kann
    ki_spielfeld=copyspielfeld()

    stupidmoves=find_stupidmoves()
    print("stupidmoves:",stupidmoves)
    x=testforpossible_doublewindmill()

    # sucht nach Sieg in 1
    if testforpossible_win(ki_spielfeld)>-1:
        zug = testforpossible_win(ki_spielfeld)

    # sucht nach Sieg in 1 des Gegners
    # wählt diesen Zug für sich selbst aus
    elif testforpossible_loss(ki_spielfeld)>-1:
        zug = testforpossible_loss(ki_spielfeld)

    # sucht nach Sieg in 2 (Zwickmühle)
    # Zwickmühle wird nicht gewählt, wenn sie zu stupidmoves gehört
    # nicht ideal; die Funktion "testforpossible_doublewindmill()" gibt nur erste Zwickmühle von links zurück
    # in einem Spezialfall könnte die entdeckte Zwickmühle ein stupidmove sein
    # rechts davon liegt aber eine, die zum Sieg führt
    elif (x>-1) and (not x in stupidmoves):
        zug=testforpossible_doublewindmill()
        print("self: trap detected")

    # sucht nach Sieg in 2 des Gegners
    # wählt diesen Zug
    elif prevent_doublewindmill()>-1:
        zug=prevent_doublewindmill()
        print("opponent: trap detected")

    # falls keine der oben genannten Züge existiert, wird ein zufälliger Zug gewählt
    # solange er kein stupidmove ist
    else:
        while True:
            zug = randint(0,6)
            if (not zeilefinden(spielfeld_lst,zug)==-1) and (not zug in stupidmoves):
                break
            

    # der Rest identisch zur Funktion "spielzug()"    
    zeile=zeilefinden(spielfeld_lst,zug)
    spielfeld_lst[zug][zeile]=spieler
    punkte_list[zug][zeile].besetzen()
    
    if gewinnprüfung(spielfeld_lst,zug,zeile):
        gewonnen()
        return
    spielerwechsel()



# fertigt Kopie von "spielfeld_lst" an
def copyspielfeld():
    global spielfeld_lst

    ki_spielfeld=[]
    for spalte in range(7):
        spaltenliste=[]
        for zeile in range(6):
            spaltenliste.append(spielfeld_lst[spalte][zeile])
        ki_spielfeld.append(spaltenliste)
    return ki_spielfeld


# gibt als Rückgabewert eine Liste mit stupidmoves
# ein stupidmove ist, wenn auf den geworfenen Stein ein weiterer Stein vom Gegner geworfen werden kann, der zum Sieg führt
# diese Züge können von "testforpossible_loss" nicht erkannt werden
def find_stupidmoves():
    liste=copyspielfeld()

    rückgabe=[]

    # wählt auf dem kopierten Spielfeld jede Zeile aus
    # und sucht für diesen zug einen möglichen Folgezug, der zur Niederlage führt
    for spalte in range(7):
        zeile=zeilefinden(liste,spalte)
        if zeile==-1:
            continue
        liste[spalte][zeile]=spieler
        if testforpossible_loss(liste)>-1:
            rückgabe.append(spalte)
        liste[spalte][zeile]=0

    # sollte jede Zeile einen stupidmove darstellen, wird die Liste leer zurückgegeben.
    if len(rückgabe)==7:
        rückgabe=[]
    return rückgabe

# sucht nach Sieg in 1        
def testforpossible_win(liste):
    global spieler

    # legt in virtuelles Spielfeld in jede Spalte einmal
    # und durchläuft Gewinnprüfung
    # bei gefundenem Sieg wird entsprechende Spalte zurückgegeben
    for spalte in range(7):
        zeile=zeilefinden(liste,spalte)
        if zeile==-1:
            continue
        liste[spalte][zeile]=spieler
        if gewinnprüfung(liste,spalte,zeile):
            liste[spalte][zeile]=0

            return spalte
        liste[spalte][zeile]=0
    return -1


# Suche nach Niederlage erfolgt analog zu Suche nach Sieg
# nur wird hier aus der Perspektive des Gegners nach einem Sieg gesucht
def testforpossible_loss(liste):
    spielerwechsel()
    x = testforpossible_win(liste)
    spielerwechsel()
    return x


# sucht nach möglicher Zwickmühle (Sieg in 2)
def testforpossible_doublewindmill():
    global spieler

    liste=copyspielfeld()
    
    for spalte in range(7):
        wins=0
        zeile=zeilefinden(liste,spalte)

        # legt auf virtuellem Spielfeld einmal in jede Spalte
        if zeile==-1:
            continue
        liste[spalte][zeile]=spieler

        # simuliert Spielerwechsel
        test_gegner=sim_spielerwechsel(spieler)

        # lässt Gegner einmal in jede Spalte werfen und untersucht Spielfeld auf Gewinnmöglichkeit
        for spalte_2 in range(7):
            zeile_2=zeilefinden(liste,spalte_2)
            if zeile==-1:
                continue
            liste[spalte_2][zeile_2]=test_gegner
          
                        
            if testforpossible_win(liste)>-1:
                wins+=1

            # 7 Gewinnmöglichkeiten bedeuten:
            # -> wenn Computer in spalte x legt, gewinnt er unabhängig vom folgenden Zug des Gegners
            # gibt spalte x zuück
            if wins==7:
                return spalte
            
            liste[spalte_2][zeile_2]=0

        
        liste[spalte][zeile]=0
    return -1


# siehe Kommentar "testforpossible_loss()"
def prevent_doublewindmill():
    spielerwechsel()
    x = testforpossible_doublewindmill()
    spielerwechsel()
    return x
        

            










################################
##############GUI###############
################################

# root formatieren
root = Tk()
root.title("Vier Gewinnt")
root.geometry("780x720")


# Bilder für Spielfeld

feldleer=PhotoImage(file="feldleer.png")
feldrot=PhotoImage(file="feldrot.png")
feldgelb=PhotoImage(file="feldgelb.png")


#Klassen

class Punkte (object):
    
    def __init__(self,posx,posy):
        self.label = Label(spielfeld, image=feldleer)
        # Koordinaten des Punktes werden umgerechnet in Werte zur Positionierung
        self.label.place(x=90*posx, y=50+90*posy, height=90, width=90)

    # gibt Punkt die Farbe des aktuellen Spielers
    def besetzen(self):
        global spieler
        if spieler==1:
            self.label.configure(image=feldrot)
        else:
            self.label.configure(image=feldgelb)
        

    # gibt Punkt leeres Bild
    def leeren(self):
        self.label.configure(image=feldleer)

class Spaltenknöpfe(object):

    # erzeugt Spaltenknöpfe
    # Koordinate des Knopfes entspricht seinem Wert
    def __init__(self,posx):
        self.button = Button(spielfeld, text = "↓",command=partial(spielzug,posx),
                                  bg="#8dc6fc")
        self.button.place(x=90*posx, y=0, height=50, width=90)
        
    def disable(self):
        self.button.config(state=DISABLED)
        
    def enable(self):
        self.button.config(state=NORMAL)


# Titelfeld
titel = Label(root, text="4 gewinnt", font=("Arial",40))
titel.place(x=10, y=10, height=50, width=630)


# Hintergrund des Spielfelds formatieren
# Punkte orientieren sich hieran
spielfeld = Label(root)
spielfeld.place(x=10, y=70, height=590, width=630)


# Punkte formatieren und in Liste speichern, damit sie einzeln ansprechbar sind
# um die Farbe zu aktualisieren
punkte_list = []

for s in range(7):
    spalten_list=[]
    for i in range(6):
        punkt = Punkte(s,i)
        spalten_list.append(punkt)
    punkte_list.append(spalten_list)


# Spaltenknöpfe platzieren und in Liste speichern
# zum aktivieren und deaktivieren
geworfenespalte=IntVar()

knöpfe_list = []

for i in range(7):
    knopf = Spaltenknöpfe(i)
    knöpfe_list.append(knopf)
    


# Gewinnanzeige
Gewinnanzeige = Label(root, bg="#8dc6fc", text="Rot am Zug", font=("Arial",30))
Gewinnanzeige.place(x=10, y=660, height=50, width=630)

# Auswahlknöpfe zur Spielweise
# 1=Pass & Play ; 2=Gegen Computer
spielweise=IntVar()
# per default auf "pass&play"
spielweise.set(1)

auswahl_rbtn1= Radiobutton(root, variable=spielweise, value=1,
                           text="Pass\n& Play", font=("Arial",20),
                           indicatoron=0, selectcolor="#8dc6fc", borderwidth=5)

auswahl_rbtn1.place(x=650, y=70, width=100)


auswahl_rbtn2=Radiobutton(root, variable=spielweise, value=2,
                          text="gegen\nComputer", font=("Arial",20),
                          indicatoron=0, selectcolor="#8dc6fc", borderwidth=5)

auswahl_rbtn2.place(x=650, y=140, width=100)

# Neustartknopf

neustart_btn=Button(root, text="Neustart", command=neustart, font=("Arial",24), activeforeground="#8dc6fc")
neustart_btn.place(x=650, y=655, height=25, width=100)

# Endeknopf
# zerstört die root

ende_btn=Button(root, text="Ende", command=root.destroy, font=("Arial",24), activeforeground="#8dc6fc")
ende_btn.place(x=650, y=685, height=25, width=100)



root.mainloop()
