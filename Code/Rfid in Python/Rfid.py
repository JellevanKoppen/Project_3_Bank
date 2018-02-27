"""
Author: Jelle van Koppen
Date: 21-2-2018
Version: 0.1
Description: Read input from arduino
"""


import serial

comm = 'COM4'

ser = serial.Serial(comm,9600)

global tagID

global digitArray
digitArray = []

def arrayReset():
    global digitArray
    digitArray = []

def idFound():
    ser.write('1'.encode())
    while True:
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        if len(result) < 5:
            integer = int(result)
            char = chr(integer)
            print(char)
            break;
        else:
            print(result)

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
    message = 1
    while True:
        if message == 1:
            print("Initiating keypad reading: ")
            message = 2
        raw = ser.readline()
        result = raw.strip().decode("utf-8")
        print(result)
        digit = result
        if(digit == '*'):
           arrayReset()
        elif(digit == '#'):
            printArray()
        else:
           digitArray.append(digit)

readRFID()
readKeypad()
