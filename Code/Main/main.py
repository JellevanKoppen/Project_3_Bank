"""
Author: Jelle van Koppen
Date: 6-3-2018
Version: 0.1
Description: main program
"""
#Modules
import _mysql
import serial
import time
import threading
import pygame

#globals
global tagID
global reading
global working
global digitArray
global reset
global tijd
global progressed
progressed = False
reset = False
reading = False
working = False

#initiate GUI
pygame.init()

#Screen measurements
display_width = 800
display_height = 600

#valueArrays
inputArray = [" "," "," ", " ", " ", " "]
digitArray = []
moneyArray = []

#initiate variables
#db = _mysql.connect(host="localhost", user="root", passwd="", db="kiwibank")
comm = 'COM4'
ser = serial.Serial(comm,9600)

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

"""DATABASE FUNCTIONS"""

def fetchDatabase(sql):
    db.query(sql)
    result = db.store_result()
    data = result.fetch_row()
    data = data[0][0].decode("utf-8")
    return data

"""END DATABASE FUNCTIONS"""

"""PYTHON->ARDUINO FUNCTIONS"""

def arrayReset():
    global digitArray
    digitArray = []

def printArray():
    global digitArray
    print(digitArray)
    arrayReset()

def write(m):
    ser.write(m.encode())

def idFound():
    write('1')  #zet arduino in tweede loop

def checkRFID():
    global reading
    global tagID
    global working
    global reset
    global tijd
    working = True
    write('1')                                  #zet arduino RFID aan (en keypad uit)
    print("CheckRFID initiated!")
    tijd = time.time()
    wrong = 0
    while working:
        print("Zoeken naar kaart")
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        if len(result) == 11:
            if result == tagID:
                write('2')
                print("Kaart gevonden!")
                reading = False
                break
            else:
                print(".")
                print("ID found: " + result)
                print("ID saved: " + tagID)
                wrong += 1
                if wrong > 3:
                    print("Te vaak fout!")
                    write('0')
                    reset = True
                    break
    print("Thread 1 Finished!")
    
def sideThread():
    global tijd
    global working
    global reset
    t2 = threading.Timer(5.0, checkRFID)
    t2.start()
    t2.join(timeout=10)
    if t2.isAlive():            
        print("Session timed_out rebooting...")
        write('0')
        reset = True
    working = False
    print("Thread 2 Finished!")
    duration = time.time() - tijd
    print("Tijdsduur: " + str(duration))

def readRFID():                                         #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    global tagID
    global progressed
    print("Bezig met rfid uitlezen")
    while True:
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        if len(result) == 11:
            print(result)
            tagID = result;
            idFound()
            break
    progressed = True

def readKeypad():
    global digitArray
    global reading
    global working
    global reset
    if reset == True:
        arrayReset()
        reset = False
        reading = False
    else:
        if reading == False:
            t1 = threading.Thread(target=sideThread)
            t1.start()
            reading = True
        if working == False:
            raw = ser.readline()
            result = raw.strip().decode("utf-8")
            print(result)
            digit = result
            if len(digit) < 3:
                if(digit == '*'):
                   arrayReset()
                elif(digit == '#'):
                    printArray()
                else:
                   digitArray.append(digit)

"""END PYTHON->ARDUINO FUNCTIONS"""

"""GUI FUNCTIONS"""

def quit_app():
    pygame.quit()
    quit()

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

def text(x,y,message, size, color):
    TextSurf, TextRect = text_objects(message, size, color)
    TextRect.center = (x,y)
    display.blit(TextSurf, TextRect)

def draw_border(x,y,w,h,c,t):#x-pos,y-pos,width,height,color,dikte
    pygame.draw.rect(display, c, (x-t, y-t, w+(t*2), h+(t*2)))

def input_amount():
    output = ""
    for x in range(0, len(moneyArray)):
        output += moneyArray[x]
    if moneyArray == []:
        pass
    else:
        output+= ",-"
    return output

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


"""END GUI FUNCTIONS"""

"""GUI WINDOWS"""
def inlog_scherm():
    global working
    global progressed
    ingelogd = False
    working = False
    while not ingelogd:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
                    
        display.fill(green_kiwi)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-100))
        display.blit(TextSurf, TextRect)

        draw_border(150, 300, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 300, 500, 75))
        TextSurf2, TextRect2 = text_objects(input_state(), largeText, black)
        TextRect2.center = ((display_width/2), (display_height/2+40))
        display.blit(TextSurf2, TextRect2)

        button("Stoppen", 325, 500, 150, 50, red_dark, red, quit_app)

        if working:
            pygame.draw.rect(display, black, (50,450,175,100))
            TextSurf3, TextRect3 = text_objects("Scanning for RFID...", verysmallText, green)
            TextRect3.center = (137, 500) 
            display.blit(TextSurf3, TextRect3)

        if not working and progressed == False:
            working = True
            t1 = threading.Thread(target=readRFID)
            t1.start()
        if progressed == True:
            working = False
            readKeypad()


        pygame.display.update()
        clock.tick(15)
    if ingelogd:
        keuze_scherm()

def keuze_scherm():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
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

        text(475,125,"Saldo:", smallText, black)
        text(575,200,"€1.000,-", largeText, black)

        draw_border(125,400,175,100, black, 2)
        draw_border(450, 400, 275, 100, black, 2)
        
        button("Opnemen", 125, 400, 175, 100, green_dark, green, geld_opnemen)
        button("Verander pincode", 450, 400, 275, 100, red_dark, red, pincode_aanpassen)
        
        
        pygame.display.update()
        clock.tick(15)

def geld_opnemen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP0:
                    moneyArray.append("1")
        
        display.fill(white)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText, black)
        TextRect.center = ((display_width/2), (display_height/2-250))
        display.blit(TextSurf, TextRect)
       
        draw_border(150, 300, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 300, 500, 75))
        TextSurf2, TextRect2 = text_objects(input_amount(), largeText, black)
        TextRect2.center = ((display_width/2), (display_height/2+40))
        display.blit(TextSurf2, TextRect2)

        button("Opnemen", 150, 500, 150, 50, green_dark, green, quit_app)
        
        button("Stoppen", 500, 500, 150, 50, red_dark, red, quit_app)
        
        pygame.display.update()
        clock.tick(15)

def pincode_aanpassen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP0:
                    moneyArray.append("1")
        
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
        

        button("Opnemen", 150, 500, 150, 50, green_dark, green, quit_app)
        
        button("Stoppen", 500, 500, 150, 50, red_dark, red, quit_app)
        
        pygame.display.update()
        clock.tick(15)


"""END GUI WINDOWS"""

"""MAIN PROGRAM"""
def main():
    while True:
        inlog_scherm()
main()
"""END MAIN PROGRAM"""
