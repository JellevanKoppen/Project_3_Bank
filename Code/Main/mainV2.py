
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
global digitArray
global pincode
global busy
global count
global alive
global keyA
global keyB
global keyC
global rows

#initiate variables
alive = True
busy = False
keyA = False
keyB = False
keyC = False
comm = 'COM8'
pincode = ""
tagID = ""
count = 0
rows = 0
values = "0123456789ABCD*#"

#initiate GUI,Database,Serial
pygame.init()
db = _mysql.connect(host="localhost", user="root", passwd="", db="kiwibank")
#ser = serial.Serial(comm,9600)

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

def selectPincode(tag):
    tag = str(tag)
    sql = "SELECT pincode FROM gebruikers WHERE tagID = '%s'" % tag
    data = fetchData(sql)
    return data

def getKlantid(pincode,tag):
    pincode = str(pincode)
    tag = str(tag)
    sql = "SELECT klantid FROM gebruikers WHERE pincode = '%s' AND tagID = '%s'" % (pincode, tag)
    data = fetchData(sql)
    return data

def getGegevens(klantid):
    klantid = str(klantid)
    sql = "SELECT naam FROM gebruikers WHERE klantid = '%s'" % klantid
    naam = fetchData(sql)
    return naam
    #sql = "geblokkeerd = SELECT geblokkeerd FROM gebruikers WHERE klantid = '%s'" % klantid
    #geblokkeerd = fetchData(sql)
    #data = (naam,geblokkeerd)
    #return data

def getRekening(klantid):
    klantid = str(klantid)
    sql = "SELECT rekeningnr FROM rekeningen WHERE klantid = '%s'" % klantid
    data = fetchData(sql)
    return data

def getSaldo():
    klantid = "5"
    rekeningnr = "1"
    rekeningnr = str(rekeningnr)
    klantid = str(klantid)
    sql = "SELECT saldo FROM rekeningen WHERE rekeningnr = '%s' AND klantid = '%s'" % (rekeningnr, klantid)
    saldo = fetchData(sql)
    return saldo
    
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

def data_entry(x,y, var, size, color):
    if var == "saldo":
        data = getSaldo()
        data = manageData(data)
        data = data[0]
    TextSurf, TextRect = text_objects(data, size, color)
    TextRect.center = (x,y)
    display.blit(TextSurf, TextRect)

def text(x,y,message, size, color):
    TextSurf, TextRect = text_objects(message, size, color)
    TextRect.center = (x,y)
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

def input_amount():
    output = ""
    for x in range(0, len(digitArray)):
        output += digitArray[x]
    if digitArray == []:
        pass
    else:
        output = '{0:,d}'.format(int(output))
        output = str(output).replace(",",".")
        output = "€" + output + ",-"
    return output


"""END GUI FUNCTIONS"""

"""GUI WINDOWS"""
def inlog_scherm():
    global tagID
    global pincode
    global busy
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

        button("Login met '#'", 325, 500, 175, 50, red_dark, red, quit_app)

        if tagID == "":
            pygame.draw.rect(display, black, (50,450,175,100))
            TextSurf3, TextRect3 = text_objects("Scanning for RFID...", verysmallText, green)
            TextRect3.center = (137, 500) 
            display.blit(TextSurf3, TextRect3)

        if not busy:
            t1 = threading.Thread(target=readThread)
            t1.start()

        if pincode == "1234":
            ingelogd = True

        pygame.display.update()
        clock.tick(15)
    if ingelogd:
        keuze_scherm()

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
             geld_opnemen()
        elif keyB:
             keyB = False
             pincode_aanpassen()

        draw_border(100,200,250,200, black, 2)
        draw_border(475, 200, 250, 200, black, 2)
        button("Opnemen", 100, 200, 250, 200, green_dark, green, keuze_scherm)
        text(325,225,"A", smallText, black)
        text(150,350,"Saldo:", smallText, black)
        data_entry(250, 350, "saldo",smallText, black)
        
        button("Verander pincode", 475, 200, 250, 200, green_dark, green, keuze_scherm)
        text(700,225,"B", smallText, black)
        
        
        pygame.display.update()
        clock.tick(15)    

def keuze_scherm():
    global keyA, keyB, keyC
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
        #text(125,175,getGegevens(),verysmallText,red)

        text(475,125,"Saldo:", smallText, black)
        text(575,200,"€1.000,-", largeText, black)

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
    global busy
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

        button("Opnemen", 150, 500, 170, 50, green_dark, green, quit_app)
        text(310,510,"A", verysmallText, black)

        button("Terug", 335, 500, 150, 50,red_dark, red, keuze_scherm)
        text(475,510,"B", verysmallText, black)
        
        button("Stoppen", 500, 500, 150, 50, red_dark, red, quit_app)
        text(640,510,"C", verysmallText, black)
        
        pygame.display.update()
        clock.tick(15)

def pincode_aanpassen():
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
        kies_rekening()
main()
"""END MAIN PROGRAM"""
