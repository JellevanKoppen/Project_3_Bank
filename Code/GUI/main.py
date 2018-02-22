"""
Author: Jelle van Koppen
Date: 22-2-2018
Version: 0.1
Description: Main GUI
"""
import pygame
from time import sleep

pygame.init()

display_width = 800
display_height = 600

inputArray = [" "," "," ", " "]

#Colors:
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
red_dark = (200, 0, 0)
green = (0, 255, 0)
green_dark = (0, 200, 0)
green_kiwi = (65,210,35)

smallText = pygame.font.Font('freesansbold.ttf', 25)
largeText = pygame.font.Font('freesansbold.ttf', 60)

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Kiwi Banking')
clock = pygame.time.Clock()

def quit_app():
    pygame.quit()
    quit()

def text_objects(text, font):
    textSurface = font.render(text, True, black)
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

    smallText = pygame.font.Font('freesansbold.ttf', 25)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x+(w/2)), (y+(h/2)))
    display.blit(textSurf, textRect)

def draw_border(x,y,w,h,c,t):
    pygame.draw.rect(display, c, (x-t, y-t, w+(t*2), h+(t*2)))

def input_state():
    output = ""
    for x in range(0, len(inputArray)):
        if inputArray[x] == " ":
            output += '- '
        else:
            output += '* '
    output.strip()
    return output

def inlog_scherm():
    ingelogd = False
    pointer = 0
    while not ingelogd:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP0 or event.key == pygame.K_0:
                    inputArray[pointer] = "0"
                    pointer += 1
                    
        display.fill(green_kiwi)
        TextSurf, TextRect = text_objects("Kiwi Banking", largeText)
        TextRect.center = ((display_width/2), (display_height/2-100))
        display.blit(TextSurf, TextRect)

        draw_border(150, 300, 500, 75, black, 2)
        pygame.draw.rect(display, white, (150, 300, 500, 75))
        TextSurf2, TextRect2 = text_objects(input_state(), largeText)
        TextRect2.center = ((display_width/2), (display_height/2+40))
        display.blit(TextSurf2, TextRect2)

        button("Stoppen", 325, 500, 150, 50, red_dark, red, quit_app)

        pygame.display.update()
        clock.tick(15)
        if pointer == 4:
            tweede_scherm()

def tweede_scherm():
    ingelogd = False
    while not ingelogd:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                    
        display.fill(red)
        TextSurf, TextRect = text_objects("Fuck You", largeText)
        TextRect.center = ((display_width/2), (display_height/2-100))
        display.blit(TextSurf, TextRect)

        pygame.display.update()
        clock.tick(15)


inlog_scherm()
