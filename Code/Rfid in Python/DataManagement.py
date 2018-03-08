"""
Author: Jelle van Koppen
Date: 21-2-2018
Version: 0.2
Description: Read input from arduino
"""


import serial

comm = 'COM4'

ser = serial.Serial(comm,9600)

values = "0123456789ABCD*#"

global tagID
global digitArray
global count

count = 0
tagID = ""
digitArray = []
reading = False
working = False

def arrayReset():
    global digitArray
    digitArray = []

def printArray():
    global digitArray
    global count
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
    if tagID == "":
        tagID = ID
    elif tagID == ID:
        return
    else:
        count += 1
        print("Found other ID")
        print("Saved ID: " + tagID)
        print("Found ID: " + ID)
        if count == 10:
            print("Too many errors, abort")

def keyFound(key):
    global digitArray
    if(key in values):
        if(key == '*'):
           arrayReset()
        elif(key == '#'):
            printArray()
        else:
           digitArray.append(key)

def readArduino():
    while True:
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


def main():
    while True:
        readArduino()

main()

