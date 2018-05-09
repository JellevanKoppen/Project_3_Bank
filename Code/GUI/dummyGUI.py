import pygame



def keuze_scherm():
    global keyA, keyB, keyC, keyD, keuze
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
        elif keyD:
             keyD = False
             geld_overmaken()

        #Alle knoppen zijn zowel klikbaar met de muis als met de keypad
        button("Opnemen", 125, 400, 175, 100, green_dark, green, geld_opnemen)
        text(285,415,"A", smallText, black)
        
        button("Verander pincode", 450, 400, 275, 100, red_dark, red, pincode_aanpassen)
        text(715,415,"B", smallText, black)

        button("Stoppen",300,525,150,60,red_dark,red,quit_app)
        text(440,540,"C",smallText,black)
        
        
        pygame.display.update()
        clock.tick(15)
