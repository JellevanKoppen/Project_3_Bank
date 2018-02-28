"""
Author: Jelle van Koppen
Date: 21-2-2018
Version: 0.1
Description: Read input from arduino
"""


import serial
import time
import threading

comm = 'COM4'

ser = serial.Serial(comm,9600)

global tagID
global reading
global working
global digitArray
global reset
reset = False
digitArray = []
reading = False
working = False

def arrayReset():
    global digitArray
    digitArray = []

def write(m):
    ser.write(m.encode())

def idFound():
    write('1')
    while True:
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        if len(result) < 5:
            print(result)
            break;
        else:
            print(result)

def catchError():
    while True:
        print("You are now catching errors!")
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        print(result)

def sideThread():
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

def checkRFID():
    global reading
    global tagID
    global working
    working = True
    write('1')
    print("CheckRFID initiated!")
    wrong = 0
    while working:
        print("Zoeken naar kaart")
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        if len(result) == 11:
            print(result)
            if tagID == result:
                write('2')
                print("Kaart gevonden!")
                reading = False
                break
            else:
                print(".")
                print("ID found: " + result)
                print("ID saved: " + tagID)
                result = ""
                wrong += 1
                if wrong > 3:
                    break;
    print("Thread 1 Finished!")
    

def printArray():
    global digitArray
    print(digitArray)
    arrayReset()

def readRFID():
    global tagID
    while True:
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        if len(result) == 11:
            print(result)
            tagID = result;
            idFound()
            break;

def readKeypad():
    global digitArray
    global reading
    global working
    global reset
    message = 1
    while not reset:
        if reading == False:
            t1 = threading.Thread(target=sideThread)
            t1.start()
            reading = True
        if working == False:
            if message == 1:
                print("Initiating keypad reading: ")
                message = 2
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
    t1.join()
    catchError()
    print("Programma beindigt!")

readRFID()
readKeypad()

