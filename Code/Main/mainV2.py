
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

#initiate variables
alive = True
busy = False
keyA = False
keyB = False
keyC = False
comm = 'COM8'
pincode = ""
keuze = ""
klantID = ""
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

def sleep():
    time.sleep(1200)
    
def timer():
    global alive
    while True:
        alive = False
        wait = threading.Thread(target=sleep)
        wait.start()
        wait.join()                    #wacht tot de sleep functie weer terug is
        if alive == False:
            print("Session Timed out!")
            quit()

"""END ADDITIONAL FUNCTIONS"""

"""DATABASE FUNCTIONS"""

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

def setPogingen(poging):
    global tagID
    tag = str(tagID)
    poging = str(poging)
    sql = "UPDATE gebruikers SET pogingen = '%s' WHERE tagID = '%s'" % (poging, tagID)
    pushData(sql)

def getKlantid():
    global klantID
    global pincode
    global tagID
    pincode = str(pincode)
    tag = str(tagID)
    sql = "SELECT klantid FROM gebruikers WHERE pincode = '%s' AND tagID = '%s'" % (pincode, tag)
    data = fetchData(sql)
    return data

def getNaam():
    global klantID
    klantid = str(klantID)
    sql = "SELECT naam FROM gebruikers WHERE klantid = '%s'" % klantid
    naam = fetchData(sql)
    return naam

def getRekening(klantid):
    klantid = str(klantid)
    sql = "SELECT rekeningnr FROM rekeningen WHERE klantid = '%s'" % klantid
    data = fetchData(sql)
    return data

def blokkeer():
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

def arrayReset():
    global digitArray
    global count
    count = 0
    digitArray = []

def printArray():
    global digitArray
    global pincode
    output = ""
    print(digitArray)
    for x in range(0, len(digitArray)):
        output += digitArray[x]
    pincode = output
    arrayReset()

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
        count += 1
        print("Found other ID")
        print("Saved ID: " + tagID)
        print("Found ID: " + ID)
        if count == 10:
            print("abort")

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

def readThread():
    global busy
    busy = True
    t1 = threading.Thread(target=readArduino)
    t1.start()
    t1.join()
    busy = False

"""END PYTHON->ARDUINO FUNCTIONS"""

"""GUI FUNCTIONS"""

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

def text(x,y,message, size, color):
    TextSurf, TextRect = text_objects(message, size, color)
    TextRect.center = (x,y)
    display.blit(TextSurf, TextRect)

def foutmelding(message):
    draw_border(50,100,700,400,black,2)
    pygame.draw.rect(display, red, (50,100,700,400))
    TextSurf, TextRect = text_objects(message, smallText, black)
    TextRect.center = (400,300)
    display.blit(TextSurf, TextRect)

def draw_border(x,y,w,h,c,t):#x-pos,y-pos,width,height,color,dikte
    pygame.draw.rect(display, c, (x-t, y-t, w+(t*2), h+(t*2)))

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

def moneyfier(output):
    output = '{0:,d}'.format(int(output))
    output = str(output).replace(",",".")
    output = "€" + output + ",-"
    return output

def input_amount():
    output = ""
    for x in range(0, len(digitArray)):
        output += digitArray[x]
    if digitArray == []:
        pass
    else:
        output = moneyfier(output)
    return output


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
def inlog_scherm():
    global tagID
    global pincode
    global busy
    global klantID
    ingelogd = False
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

        draw_border(150, 300, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 300, 500, 75))
        TextSurf2, TextRect2 = text_objects(input_state(), largeText, black)
        TextRect2.center = ((display_width/2), (display_height/2+40))
        display.blit(TextSurf2, TextRect2)
        text(400,500,"Inloggen: '#' | Correctie: '*'", smallText, black)

        if tagID == "":
            pygame.draw.rect(display, black, (50,450,175,100))
            TextSurf3, TextRect3 = text_objects("Scanning for RFID...", verysmallText, green)
            TextRect3.center = (137, 500) 
            display.blit(TextSurf3, TextRect3)
        else:
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
            

        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        if pincode != "":
            klant = getKlantid()
            klant = manageData(klant)
            try:
                klantID = klant[0]
                print("KlantID gevonden: " + klantID)
                pincode = ""
            except IndexError:
                print("Geen klantID gevonden")
                pogingen = int(pogingen)
                pogingen += 1
                pincode = ""
                if pogingen >= 3:
                    blokkeer()
                else:
                    print("Setting pogingen to: "+str(pogingen))
                    setPogingen(str(pogingen))
            if klantID != "":
                ingelogd = True
                pincode = ""
            else:
                print("Kaart niet gevonden")

        pygame.display.update()
        clock.tick(15)
    if ingelogd:
        kies_rekening()

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

        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        if keyA:
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
        data_entry(200,175, "naam",0, verysmallText, black)

        text(475,125,"Saldo:", smallText, black)
        data_entry(575, 200, "saldo",keuze,largeText, black)
        

        draw_border(125,400,175,100, black, 2)
        draw_border(450, 400, 275, 100, black, 2)

        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        if keyA:
             keyA = False
             geld_opnemen()
        elif keyB:
             keyB = False
             pincode_aanpassen()
        
        button("Opnemen", 125, 400, 175, 100, green_dark, green, geld_opnemen)
        text(285,415,"A", smallText, black)
        
        button("Verander pincode", 450, 400, 275, 100, red_dark, red, pincode_aanpassen)
        text(715,415,"B", smallText, black)
        
        
        pygame.display.update()
        clock.tick(15)

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

        if keyA:
            keyA = False
            opnemen()
        elif keyB:
            keyB = False
            keuze_scherm()
        elif keyC:
            keyC = False
            quit_app()

        if pincode != "":
            bedrag = pincode
            pincode = ""
            print (bedrag)
            print (keuze)
            if keuze == 1:
                rekening = 0
            else:
                rekening = 1
            saldo = getSaldo()
            saldo = saldo[rekening][0][0].decode("utf-8")
            saldo = int(saldo)
            if saldo == 0:
                print("Te weinig saldo!")
            print (saldo)
            

        button("Opnemen", 150, 500, 170, 50, green_dark, green, opnemen)
        text(310,510,"#", verysmallText, black)

        button("Terug", 335, 500, 150, 50,red_dark, red, keuze_scherm)
        text(475,510,"B", verysmallText, black)
        
        button("Stoppen", 500, 500, 150, 50, red_dark, red, quit_app)
        text(640,510,"C", verysmallText, black)
        
        pygame.display.update()
        clock.tick(15)

def pincode_aanpassen():
    global busy, keyA, keyB, keyC
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_app()
        
        display.fill(white)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-250))
        display.blit(TextSurf, TextRect)
       
        draw_border(150, 150, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 150, 500, 75))
        TextSurf2, TextRect2 = text_objects(input_amount(), largeText, black)
        TextRect2.center = ((display_width/2), (display_height/2-50))
        display.blit(TextSurf2, TextRect2)

        draw_border(150, 300, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 300, 500, 75))
        TextSurf3, TextRect3 = text_objects(input_amount(), largeText, black)
        TextRect3.center = ((display_width/2), (display_height/2+50))
        display.blit(TextSurf3, TextRect3)

        if keyA:
            keyA = False
            quit_app()
        elif keyB:
            keyB = False
            keuze_scherm()
        elif keyC:
            keyC = False
            quit_app()
            
        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        button("Veranderen", 150, 500, 170, 50, green_dark, green, quit_app)
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
