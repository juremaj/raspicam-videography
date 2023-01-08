import serial
import matplotlib.pyplot as plt

def read_serial_data():
    ser = serial.Serial("/dev/ttyACM0", 9600)   #specify your port and braudrate
    data = ser.read()           #read byte from serial device
    print(data)                               #display the read byte

    return data

def plot_all_data(all_data):
    plt.plot(all_data)
    plt.show()
    plt.xlabel('Time(s)')

all_data = []

while len(all_data) < 1000:
    data = read_serial_data()
    all_data.append(int(data))

plot_all_data(all_data)