import threading
import socket
import os
from datetime import datetime


class Sensor:
    def __init__(self, addr, port, name):
        self.name = name
        self.thread = threading.Thread(target=self.read)
        self.socket = self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = addr
        self.port = port
        self.last_measurement = ''

    def read(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.address, self.port))
        recv = self.socket.recv(100)
        self.last_measurement = hex(int(datetime.now().timestamp())) + " " + recv.decode()
        return recv.decode()

    def start_thread(self):
        self.thread = threading.Thread(target=self.read)
        self.thread.start()

    def __str__(self):
        return self.name


sensors = [
    # Sensor("10.2.1.17", 8080, "Alcyone"),
    Sensor("10.2.1.51", 8080, "Atlas"),
    # Sensor("10.26.142.9", 8080, "Atlas"),
    # Sensor("10.2.1.54", 8080, "Asterope"),
    # Sensor("10.2.1.57", 8080, "Celaeno"),
    Sensor("10.2.1.59", 8080, "Maia"),
    # Sensor("0.0.0.0", 8080, "Taygeta"),  # :(
]

if not os.path.isdir('sensorlogs'):
    os.mkdir('sensorlogs')
    for sensor in sensors:
        with open('sensorlogs/' + sensor.name + '.csv', 'x') as f:
            f.write('hextimestamp,temp,light,sound,pressure,humidity\n')


def pad(s, n):
    return str((n - len(s)) * ' ') + s


def print_all_data():
    i = 0
    for s in sensors:
        print(pad(str(s), 10), end=': ')
        for m in s.last_measurement.split()[1:]:
            print(pad(m, 10), end=' ')
        else:
            print()
        i += 1


def clear():
    os.system('cls')


# TODO: Make more of these and use them
def convert_temp(t):
    return ((((t * 5000.0) / 1024.0) - 600.0) / 10.0) / 2


def convert_sound(s):
    return s - 247


def read_loop():
    for s in sensors:
        s.read()
        with open('sensorlogs/' + s.name + '.csv', 'a') as file:
            file.write(','.join(s.last_measurement.split()) + '\n')
        print_all_data()
        # time.sleep(0.15)


print("       Name       Temp      Light      Sound   Pressure   Humidity")
while True:
    read_loop()
