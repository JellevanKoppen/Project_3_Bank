"""
Author: Jelle van Koppen
Date: 6-3-2018
Version: 2.0
Description: main program

This program does not include the database
"""
#Modules
import serial
import pygame
import threading
import time

#globals
global tagID
global digitArray
global pincode
global busy
global count
global alive

#initiate variables
alive = True
busy = False
comm = 'COM4'
ser = serial.Serial(comm,9600)
pincode = ""
tagID = ""
count = 0
values = "0123456789ABCD*#"

#initiate GUI
pygame.init()

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
    time.sleep(15)
    
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
    global alive
    if(key in values):
        alive = True
        if(key == '*'):
           arrayReset()
        elif(key == '#'):
            printArray()
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
    global busy
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
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
        print("Booting up...")
        timeout = threading.Thread(target=timer)
        timeout.start()
        inlog_scherm()        
main()
"""END MAIN PROGRAM"""
