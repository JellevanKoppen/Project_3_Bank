"""
Author: Jelle van Koppen
Date: 21-2-2018
Version: 0.1
Description: Read input from arduino
"""
import serial

comm = 'COM8'

ser = serial.Serial(comm,9600)

pointer = 0
digitArray = []

while True:
    digit = ser.readline()
    if(digit):
        digit.strip()
        if(digit == '#'):
           arrayReset()
        else:
           digitArray[pointer] = str(digit)
        print (message)


def arrayReset():
    for x in range(0, pointer):
           digitArray[x] = ""
    pointer = 0
