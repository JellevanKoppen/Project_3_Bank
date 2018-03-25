
"""
Author: Jelle van Koppen
Date: 6-3-2018
Version: 2.0
Description: main program
"""
#Modules
import serial
import pygame
import threading
import time
import _mysql

#globals
global tagID
global klantID
global digitArray
global pincode
global busy
global count
global alive
global keyA
global keyB
global keyC
global rows
global keuze
global volgende
global pogingen

#initiate variables
volgende = False
alive = True
busy = False
keyA = False
keyB = False
keyC = False
comm = 'COM8'
pincode = ""
keuze = ""
klantID = "5"
tagID = ""
count = 0
rows = 0
values = "0123456789ABCD*#"

#initiate GUI,Database,Serial
pygame.init()
db = _mysql.connect(host="localhost", user="root", passwd="", db="kiwibank")
ser = serial.Serial(comm,9600)

#Screen measurements
display_width = 800
display_height = 600

#valueArrays
inputArray = [" "," "," ", " ", " ", " "]
digitArray = []

#Colors
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
red_dark = (200, 0, 0)
green = (0, 255, 0)
green_dark = (0, 200, 0)
green_kiwi = (65,210,35)

#Fonts
verysmallText = pygame.font.Font('freesansbold.ttf', 15)
smallText = pygame.font.Font('freesansbold.ttf', 25)
largeText = pygame.font.Font('freesansbold.ttf', 60)

#Set screen options
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Kiwi Banking')
img = pygame.image.load('kiwi.jpg')
pygame.display.set_icon(img)
clock = pygame.time.Clock()

"""ADDITIONAL FUCNTIONS"""

#Een functie die ervoor zorgt dat na twee minuten de gebruiker wordt uitgelogd
#Dit gebeurd alleen als er voor twee minuten geen interactie is met de keypad of rfid

def sleep():
    time.sleep(60)
    
def timer():
    global alive
    while True:
        alive = False
        wait = threading.Thread(target=sleep)
        wait.start()
        wait.join()                    #wacht tot de sleep functie weer terug is
        if alive == False:
            print("Session Timed out!") #Als er geen interactie is geweest wordt de gebruiker uitgelogd
            quit_app()

"""END ADDITIONAL FUNCTIONS"""

"""DATABASE FUNCTIONS"""

#Een verdere beschrijving van de functies is te vinden in de:
#Database_Python.py

def fetchData(sql):
    data = []
    global rows
    db.query(sql)
    result = db.store_result()
    rows = result.num_rows()
    for x in range(0,rows):
        data.append(result.fetch_row())
    return data

def pushData(sql):
    db.query(sql)

def selectPincode():
    global tagID
    tag = str(tagID)
    sql = "SELECT pincode FROM gebruikers WHERE tagID = '%s'" % tag
    data = fetchData(sql)
    return data

def setPincode(pincode):
    global klantID
    pincode = str(pincode)
    klantid = str(klantID)
    sql = "UPDATE gebruikers SET pincode = '%s' WHERE klantid = '%s'" % (pincode, klantid)
    data = pushData(sql)

def getGeblokkeerd():
    global tagID
    tag = str(tagID)
    sql = "SELECT geblokkeerd FROM gebruikers WHERE tagID = '%s'" % tag
    data = fetchData(sql)
    return data

def getPogingen():
    global tagID
    tag = str(tagID)
    sql = "SELECT pogingen FROM gebruikers WHERE tagID = '%s'" % tag
    data = fetchData(sql)
    return data

def setPogingen(poging): #Zet de pogingen hoger als de pincode fout ingetoetst is
    global tagID
    tag = str(tagID)
    poging = str(poging)
    sql = "UPDATE gebruikers SET pogingen = '%s' WHERE tagID = '%s'" % (poging, tagID)
    pushData(sql)

def getKlantid():   #Selecteert klantid van de gebruikers
    global klantID
    global pincode
    global tagID
    pincode = str(pincode)
    tag = str(tagID)
    sql = "SELECT klantid FROM gebruikers WHERE pincode = '%s' AND tagID = '%s'" % (pincode, tag)
    data = fetchData(sql)
    return data

def getNaam():      #Selecteert de naam van de gebruiker
    global klantID
    klantid = str(klantID)
    sql = "SELECT naam FROM gebruikers WHERE klantid = '%s'" % klantid
    naam = fetchData(sql)
    return naam

def getRekening():  #Selecteert de rekeningen van de gebruiker
    global klantID
    klantid = str(klantID)
    sql = "SELECT rekeningnr FROM rekeningen WHERE klantid = '%s'" % klantid
    data = fetchData(sql)
    return data

def blokkeer(): #Checkt of de gebruiker geblokkeerd is
    global tagID
    tag = str(tagID)
    sql = "UPDATE gebruikers SET geblokkeerd = 'ja' WHERE tagID = '%s'" % tagID
    pushData(sql)

def getSaldo():   #Geeft het saldo van één rekeningnummer
    global klantID
    klantid = str(klantID)
    sql = "SELECT saldo FROM rekeningen WHERE klantid = '%s'" % klantid
    saldo = fetchData(sql)
    return saldo

def opnemen(rekeningnr, saldo):
    rekeningnr = str(rekeningnr)
    saldo = str(saldo)
    sql = "UPDATE rekeningen SET saldo = '%s' WHERE rekeningnr = '%s'" % (saldo, rekeningnr)
    pushData(sql)
    sql = "SELECT saldo FROM rekeningen WHERE rekeningnr = '%s'" % rekeningnr
    data = fetchData(sql)
    return data
    
def manageData(data):
    result = []
    global rows
    try:
        for x in range(0,rows):
            result.append(data[x][0][0])
        return result
    except IndexError:
        print("Error geen data gevonden")

"""END DATABASE FUNCTIONS"""

"""PYTHON->ARDUINO FUNCTIONS"""

#Reset de array zodat er opnieuw ingelogt kan worden
def arrayReset():
    global digitArray
    global count
    global volgende
    count = 0
    digitArray = []


#Print de array in de console en zet de output als pincode
def printArray():
    global digitArray
    global pincode
    output = ""
    print(digitArray)
    for x in range(0, len(digitArray)):
        output += digitArray[x]
    pincode = output
    arrayReset()

    
#Checkt of de id overeen komt met de id opgeslagen in het programma
#Als er geen id bekend is wordt deze gezet als opgeslagen id
def idFound(ID):
    global tagID
    global count
    global alive
    if tagID == "":
        tagID = ID
    elif tagID == ID:
        count = 0
        alive = True
        return
    else:
        if count == 10:
            print("abort")
            quit_app()
        else:
            count += 1
            print("Found other ID")
            print("Saved ID: " + tagID)
            print("Found ID: " + ID)


#Elke key die de keypad stuurt gaat door deze functie
#Deze functie kijkt of er een letter,* of # gedrukt is en handeld hierop zoals aangegeven
#Elke andere key wordt toegevoegd aan de pincode array
def keyFound(key):
    global digitArray
    global keyA
    global keyB
    global keyC
    global alive
    if(key in values):
        alive = True
        if(key == '*'):
           arrayReset()
        elif(key == '#'):
            printArray()
        elif(key == 'A'):
             keyA = True
        elif(key == 'B'):
             keyB = True
        elif(key == 'C'):
             keyC = True
        else:
            digitArray.append(key)


#De hoofdfunctie van de arduino!
#Bepaald of er een RFID Tag of een Key binnen komt en stuurt deze
#naar bijbehoorende functies
def readArduino():
    raw = ser.readline()
    result = raw.strip().decode("utf-8")
    if len(result) == 11:
        print(result)
        idFound(result)
    elif len(result) == 1:
        print(result)
        keyFound(result)
    else:
        print("Nonsense:")
        print(result)

#Een sidethread zodat de GUI loop ongestoord door kan werken
def readThread():
    global busy
    busy = True
    t1 = threading.Thread(target=readArduino)
    t1.start()
    t1.join()
    busy = False

"""END PYTHON->ARDUINO FUNCTIONS"""

"""GUI FUNCTIONS"""

#Brengt de GUI terug naar het inlogscherm en reset de gegevens
def quit_app():
    inlog_scherm()
    arrayReset()

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def button(msg,x,y,w,h,ic,ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(display, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(display, ic, (x, y, w, h))

    textSurf, textRect = text_objects(msg, smallText, black)
    textRect.center = ((x+(w/2)), (y+(h/2)))
    display.blit(textSurf, textRect)

#Kijkt naar de var en opent de bijbehorende functie
#De functie haalt vervolgens gegevens op uit de database
#om deze gegevens vervolgens klaar te maken om deze op het scherm weer te geven
def data_entry(x,y, var,row, size, color):
    if var == "saldo":
        data = getSaldo()
        data = manageData(data)
        data = data[row-1]
        data = moneyfier(data)
    if var == "naam":
        data = getNaam()
        data = manageData(data)
        data = data[row]
    TextSurf, TextRect = text_objects(data, size, color)
    TextRect.center = (x,y)
    display.blit(TextSurf, TextRect)

#Een functie die tekst weergeeft op het scherm op een meegegeven x,y positie
def text(x,y,message, size, color):
    TextSurf, TextRect = text_objects(message, size, color)
    TextRect.center = (x,y)
    display.blit(TextSurf, TextRect)

#Een foutmelding die een bericht op het scherm laat zien
def foutmelding(message):
    draw_border(50,100,700,400,black,2)
    pygame.draw.rect(display, red, (50,100,700,400))
    TextSurf, TextRect = text_objects(message, smallText, black)
    TextRect.center = (400,300)
    display.blit(TextSurf, TextRect)

#Een functie die ervoor zorgt dat er een mooi randje om een rechthoek getekend wordt
def draw_border(x,y,w,h,c,t):#x-pos,y-pos,width,height,color,dikte
    pygame.draw.rect(display, c, (x-t, y-t, w+(t*2), h+(t*2)))

#De status van de inlogbalk.
#Deze functie zorgt ervoor dat er een * of een - op het scherm wordt afgedrukt
#wat overeen komt met hoeveel getallen zijn ingevoerd
def input_state():
    output = ""
    for x in range(0, len(inputArray)):
        try:
            if digitArray[x] is not None:
                output += '* '
            else:
                raise IndexError
        except IndexError:
            output += '- '
    output.strip()
    return output

#Neemt een getal, zet tussen de duizendtallen een '.' en zorgt voor de € en ,- tekens aan het begin en eind
def moneyfier(output):
    output = '{0:,d}'.format(int(output))
    output = str(output).replace(",",".")
    output = "€" + output + ",-"
    return output

#Neemt een array en zet deze om in een geldgetal
def input_amount():
    output = ""
    for x in range(0, len(digitArray)):
        output += digitArray[x]
    if digitArray == []:
        pass
    else:
        output = moneyfier(output)
    return output

#Slaat de keuze op voor welke rekening is gekozen
#(Het getal komt overeen met de rij uit de database)
def keuze1():
    global keuze
    keuze = 0
    keuze_scherm()

def keuze2():
    global keuze
    keuze = 1
    keuze_scherm()

"""END GUI FUNCTIONS"""

"""GUI WINDOWS"""
#Het inlogscherm waar de RFID en pincode wordt gecheckt
#Voor een duidelijkere uitleg staat er in de mainGUI.py ook nog een beschrijving over dezelfde functies
def inlog_scherm():
    global tagID
    global pincode
    global busy
    global klantID
    global pogingen
    ingelogd = False
    tagID = ""
    print("Welcome")
    print("Present RFID card")
    while not ingelogd:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_app()
                    
        display.fill(green_kiwi)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-100))
        display.blit(TextSurf, TextRect)

        if tagID == "":
            pygame.draw.rect(display, black, (50,450,175,100))
            TextSurf3, TextRect3 = text_objects("Scanning for RFID...", verysmallText, green)
            TextRect3.center = (137, 500) 
            display.blit(TextSurf3, TextRect3)
       else:
            draw_border(150, 300, 500, 75, black, 2)
            pygame.draw.rect(display, white, (150, 300, 500, 75))
            TextSurf2, TextRect2 = text_objects(input_state(), largeText, black)
            TextRect2.center = ((display_width/2), (display_height/2+40))
            display.blit(TextSurf2, TextRect2)
            text(400,500,"Inloggen: '#' | Correctie: '*'", smallText, black)
            geblokkeerd = getGeblokkeerd()
            geblokkeerd = manageData(geblokkeerd)
            geblokkeerd = geblokkeerd[0]
            geblokkeerd = geblokkeerd.decode("utf-8")
            if geblokkeerd == "ja":
                foutmelding("Deze pas is geblokkeerd, u kunt geen geld uitnemen")
            pogingen = getPogingen()
            pogingen = manageData(pogingen)
            pogingen = pogingen[0]
            pogingen = pogingen.decode("utf-8")
            

        if not busy:    #Als er niet serieel wordt uitgelezen wordt dit programma gelijk weer opgestart
            t1 = threading.Thread(target=readThread) #Dit wordt gedaan in een sidethread zodat deze loop gewoon door kan gaan
            t1.start()

        if pincode != "":   #Zodra er een pincode is ingevoerd wordt deze functie opgeroepen
            klant = getKlantid()
            klant = manageData(klant)   #Dit geeft een kaal getal terug (Bijvoorbeeld 5) dit is dan het klantid
            try:
                klantID = klant[0]
                print("KlantID gevonden: " + klantID)
                pincode = ""
            except IndexError:          #Wanneer er geen id gevonden is betekend dit dat er geen bestaat en/of dat de pincode fout is
                ingelogd = False
                klantID = ""
                print("Geen klantID gevonden")
                pogingen = int(pogingen)
                pogingen += 1
                pincode = ""
                if pogingen >= 3:       #Na drie keer wordt de pas geblokkeerd
                    blokkeer()
                else:
                    print("Setting pogingen to: "+str(pogingen)) #Bij een foute pincode wordt meteen een poging opgeslagen zodat er
                    setPogingen(str(pogingen))                   #niet onbeperkt geprobeerd kan worden
            if klantID != "":
                ingelogd = True
                setPogingen("0")
                pincode = ""
            else:
                print("Pincode fout")   #Een bevestiging dat de pincode fout was

        pygame.display.update()
        clock.tick(15)
    if ingelogd:
        kies_rekening()                 #Start het volgende scherm

#Hier wordt een keuze gemaakt uit de twee rekeningen op de naam van de klant
def kies_rekening():
    global keyA, keyB, keyC
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_app()
        
        display.fill(white)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-250))
        display.blit(TextSurf, TextRect)

        if not busy:    #Omdat er een keuze gemaakt moet worden is deze functie weer nodig
            t1 = threading.Thread(target=readThread)#om de keypad weer uit te lezen.
            t1.start()

        if keyA:            #Als er een A of B wordt ingedrukt worden de bijbehorende functies gestart
             keyA = False
             keuze1()
        elif keyB:
             keyB = False
             keuze2()

        draw_border(100,200,250,200, black, 2)
        draw_border(475, 200, 250, 200, black, 2)
        button("Rekening 1", 100, 200, 250, 200, green_dark, green, keuze1)
        text(325,225,"A", smallText, black)
        text(150,350,"Saldo:", smallText, black)
        data_entry(250, 350, "saldo",0,smallText, black)
        
        button("Rekening 2", 475, 200, 250, 200, green_dark, green, keuze2)
        text(700,225,"B", smallText, black)
        text(525,350,"Saldo:", smallText, black)
        data_entry(625, 350, "saldo",1,smallText, black)
        
        
        pygame.display.update()
        clock.tick(15)    

#Dit is het keuzemenu, hier worden de gegevens aan je laten zien, je saldo weergegeven en
#je kan een keuze maken of je je pincode wil aanpassen of geld wil opnemen
def keuze_scherm():
    global keyA, keyB, keyC, keuze
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_app()
        
        display.fill(white)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-250))
        display.blit(TextSurf, TextRect)

        pygame.draw.rect(display, green_kiwi, (50, 100, 325,200))
        pygame.draw.rect(display, green_kiwi, (425, 100, 325,200))
        pygame.draw.rect(display, green_kiwi, (50, 350, 325,200))
        pygame.draw.rect(display, green_kiwi, (425, 350, 325,200))

        text(125,125,"Gegevens:", smallText, black)
        text(85,175,"naam:", verysmallText, black)
        data_entry(200,175, "naam",0, verysmallText, black) #Data_entry haalt de gegevens aan de database

        text(475,125,"Saldo:", smallText, black)
        data_entry(575, 200, "saldo",keuze,largeText, black)#Het meegegeven keyword saldo zorgt ervoor dat de juiste gegevens worden opgehaald
        

        draw_border(125,400,175,100, black, 2)      #Dit zijn de randen om de knoppen heen
        draw_border(450, 400, 275, 100, black, 2)
        draw_border(300,525,150,60,black, 2)

        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        if keyA:
             keyA = False
             geld_opnemen()
        elif keyB:
             keyB = False
             pincode_aanpassen()
        elif keyC:
             keyC = False
             quit_app()

        #Alle knoppen zijn zowel klikbaar met de muis als met de keypad
        button("Opnemen", 125, 400, 175, 100, green_dark, green, geld_opnemen)
        text(285,415,"A", smallText, black)
        
        button("Verander pincode", 450, 400, 275, 100, red_dark, red, pincode_aanpassen)
        text(715,415,"B", smallText, black)

        button("Stoppen",300,525,150,60,red_dark,red,quit_app)
        text(440,540,"C",smallText,black)
        
        
        pygame.display.update()
        clock.tick(15)

#Functie om geld op te nemen
#Met het invoeren van een getal wordt het gelijk van de rekening gehaald
def geld_opnemen():
    global busy, keyA, keyB, keyC, pincode, keuze
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_app()
        
        display.fill(white)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-250))
        display.blit(TextSurf, TextRect)
       
        draw_border(150, 300, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 300, 500, 75))
        TextSurf2, TextRect2 = text_objects(input_amount(), largeText, black)
        TextRect2.center = ((display_width/2), (display_height/2+40))
        display.blit(TextSurf2, TextRect2)

        pygame.draw.rect(display, white, ((display_width/2-125),(display_height/2-20),250,30))

        text((display_width/2),(display_height/2),"Voer hoeveelheid in", smallText, black)

        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        elif keyB:
            keyB = False
            keuze_scherm()
        elif keyC:
            keyC = False
            quit_app()

        if pincode != "":
            bedrag = int(pincode)
            pincode = ""
            print (bedrag)
            if keuze == 1:
                rekening = 0
            else:
                rekening = 1
            rekeningnr = getRekening()
            rekeningnr = manageData(rekeningnr)
            print(rekeningnr)

            #saldo wordt opgehaald en omgerekend naar een integer
            saldo = getSaldo()
            saldo = saldo[rekening][0][0].decode("utf-8")
            saldo = int(saldo)
            #Dezei if statement kijkt of je genoeg op je rekening hebt voor een geldopname
            if saldo <= 0 or saldo-bedrag < 0:
                print("Te weinig saldo!")
                foutmelding("Te weinig saldo!")
                time.sleep(3)
                keuze_scherm()

            #Zo ja dan wordt je nieuwe saldo berekend en verwerkt in de database
            saldo -= bedrag
            saldo = str(saldo)
            print("Nieuw saldo: "+saldo)
            opnemen(rekeningnr[rekening], saldo)
            keuze_scherm()

        button("Opnemen", 150, 500, 170, 50, green_dark, green, opnemen)
        text(310,510,"#", verysmallText, black)

        button("Terug", 335, 500, 150, 50,red_dark, red, keuze_scherm)
        text(475,510,"B", verysmallText, black)
        
        button("Stoppen", 500, 500, 150, 50, red_dark, red, quit_app)
        text(640,510,"C", verysmallText, black)
        
        pygame.display.update()
        clock.tick(15)


#Functie om je pincode aan te passen
def pincode_aanpassen():
    global busy, keyA, keyB, keyC, volgende, pincode
    volgende = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_app()
        
        display.fill(white)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-250))
        display.blit(TextSurf, TextRect)

        if keyA:
            keyA = False
            printArray()
            
        elif keyB:
            keyB = False
            keuze_scherm()
        elif keyC:
            keyC = False
            quit_app()
            
        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        text((display_width/2),(display_height/2-35),"Volgende: '#', Correctie: '*'", verysmallText, black)

        if pincode != "":
            if volgende:
                temp = selectPincode()
                temp = manageData(temp)
                temp = temp[0]
                temp = str(temp.decode("utf-8"))
                if temp == oude_pincode:
                    print("Pincode Gewijzigt!")
                    setPincode(pincode)
                    pincode = ""
                    keuze_scherm()
                else:
                    print("Pincode komt niet overeen!")
                    pincode == ""
            volgende = True
            oude_pincode = pincode
            pincode = ""
        elif not volgende:
            #Eerst wordt de oude pincode ingevuld (de nieuwe pincode is nog niet te zien om verwarring te voorkomen)
            draw_border(150, 150, 500, 75, black, 2)
            pygame.draw.rect(display, white, (150, 150, 500, 75))
            TextSurf2, TextRect2 = text_objects(input_state(), largeText, black)
            TextRect2.center = ((display_width/2), (display_height/2-100))
            display.blit(TextSurf2, TextRect2)
            pygame.draw.rect(display, white, ((display_width/2-150),(display_height/2-165),300,30))
            text((display_width/2),(display_height/2-150),"Voer huidige pincode in", smallText, black)
            
        if volgende:
            #Zodra code is ingevuld kun je een nieuwe code invullen. Deze wordt gelijk veranderd in de database
            draw_border(150, 300, 500, 75, black, 2)
            pygame.draw.rect(display, white, ((display_width/2-150),(display_height/2-20),300,30))
            pygame.draw.rect(display, white, (150, 300, 500, 75))
            TextSurf3, TextRect3 = text_objects(input_state(), largeText, black)
            TextRect3.center = ((display_width/2), (display_height/2+50))
            display.blit(TextSurf3, TextRect3)
            text((display_width/2),(display_height/2),"Voer nieuwe pincode in", smallText, black)

        button("Veranderen", 150, 500, 170, 50, green_dark, green, printArray)
        text(310,510,"A", verysmallText, black)

        button("Terug", 335, 500, 150, 50,red_dark, red, keuze_scherm)
        text(475,510,"B", verysmallText, black)
        
        button("Stoppen", 500, 500, 150, 50, red_dark, red, quit_app)
        text(640,510,"C", verysmallText, black)
        
        pygame.display.update()
        clock.tick(15)


"""END GUI WINDOWS"""

"""MAIN PROGRAM"""
def main():
    while True:
        print("Booting up...")
        timeout = threading.Thread(target=timer)
        timeout.start()
        inlog_scherm()
main()
"""END MAIN PROGRAM"""
