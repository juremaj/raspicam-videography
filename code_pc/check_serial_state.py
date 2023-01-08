import serial
import time

def read_serial_data():
    ser = serial.Serial("/dev/ttyACM0", 9600)   #specify your port and braudrate
    data = ser.read()                         #read byte from serial device
    print(data)                               #display the read byte

while True:
    read_serial_data()