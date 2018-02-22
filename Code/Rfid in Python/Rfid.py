"""
Author: Jelle van Koppen
Date: 21-2-2018
Version: 0.1
Description: Read input from arduino
"""
import serial

comm = 'COM8'

ser = serial.Serial(comm,9600)

while True:
    message = ser.readline()
    message.strip()
    print (message)
