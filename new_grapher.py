import os
import socket
import sys
import platform
import threading
import time
from datetime import datetime


class Sensor:
    """
    Object to handle individual sensor modules.

    :param addr: IP address of the sensor
    :param port: Port of the sensor
    :param name: Name of the board
    :return: Sensor object
    """
    def __init__(self, addr, port, name):
        self.name = name
        self.thread = threading.Thread(target=self.read)
        self.socket = self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = addr
        self.port = port
        self.last_measurement = ''

    def read(self):
        """
        Read data from the sensor into Measurement objects

        :return: Decoded data.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.address, self.port))
        recv = self.socket.recv(100)
        self.last_measurement = hex(int(datetime.now().timestamp())) + " " + recv.decode()
        return recv.decode()

    def start_thread(self):
        """
        Starts the read process in a separate thread.
        """
        self.thread = threading.Thread(target=self.read)
        self.thread.start()

    def __str__(self):
        return self.name


def pad(s, n):
    """
    Pads a string to a certain length with leading spaces.
    :param s: String to pad
    :param n: Pad length
    :return: Padded string
    """
    return str((n - len(s)) * ' ') + s


def print_all_data(current_sensor):
    """
    Prints data for the sensors.

    :param current_sensor: Index of the most recently updated sensor
    :return: None
    """
    print("       Name       Temp      Light      Sound   Pressure   Humidity")
    i = 0
    for s in sensor_set:
        print(pad(str(s), 10), end=': ')
        for m in s.last_measurement.split()[1:]:
            print(pad(m, 10), end=' ')
        if i == current_sensor:
            print('<')
        else:
            print()
        i += 1


def clear():
    """
    Clears the screen using the system cls method -- windows only
    :return:
    """
    if platform.system() == 'Windows':
        os.system('cls')
    elif platform.system() == 'Linux':
        print(chr(27) + "[2J")


# TODO: Make more of these and use them
def convert_temp(t):
    """
    Converts an analog temperature value to the Celsius scale. Calibrated for a particular sensor.

    :param t: Analog temperature value
    :return: Celsius value
    """
    return ((((t * 5000.0) / 1024.0) - 600.0) / 10.0) / 2


def convert_sound(s):
    """
    Stub

    :param s: Input analog sound value
    :return: Output decibel value
    """
    return s - 247


def read_loop():
    """
    The main read loop. Called recursively.
    """
    current_sensor = 0
    for s in sensor_set:
        sys.stdout.flush()  # This probably does something
        s.read()
        with open('sensorlogs/' + s.name + '.csv', 'a') as file:
            file.write(','.join(s.last_measurement.split()) + '\n')
        if len(sensor_set) > 1:
            current_sensor += 1
            current_sensor %= len(sensor_set)
        clear()
        print_all_data(current_sensor)
        if len(sensor_set) == 1:
            # Stops the server overloading the board with sequential requests.
            # If there are multiple boards, the time taken with every board is enough to overcome this.
            time.sleep(0.15)


if __name__ == "__main__":
    location = 1
    sensors = [
        Sensor("10.2.1.17", 8080, "Alcyone"),
        Sensor("10.2.1.51", 8080, "Atlas"),
        Sensor("10.2.1.54", 8080, "Asterope"),
        Sensor("10.2.1.57", 8080, "Celaeno"),
        Sensor("10.2.1.59", 8080, "Maia"),
        # Sensor("0.0.0.0", 8080, "Taygeta"),  # :(
    ]
    sensors_ghs = [
        Sensor("10.26.141.109", 8080, "Alcyone"),
        Sensor("10.26.141.76", 8080, "Atlas"),
        Sensor("10.26.141.187", 8080, "Celaeno"),
        Sensor("10.26.141.38", 8080, "Maia"),
    ]

    if location == 1:
        sensor_set = sensors_ghs
    else:
        sensor_set = sensors

    os.system("mode con: cols=70 lines=" + str(len(sensor_set) + 2))

    if not os.path.isdir('sensorlogs'):
        os.mkdir('sensorlogs')
        for sensor in sensor_set:
            with open('sensorlogs/' + sensor.name + '.csv', 'x') as f:
                f.write('hextimestamp,temp,light,sound,pressure,humidity\n')

    while True:
        read_loop()
