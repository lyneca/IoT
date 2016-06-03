import time

import threading
from datetime import datetime
from tkinter import *

import argparse
import requests
import requests.adapters
import requests.exceptions

d_time = time.time()


def debug(s, l=0, i=False):
    """
    Debug print shorthand function

    :param s: print string
    :param l: error level
    :param i: is the message priority (i.e. will it be displayed no matter what)?
    :return: None
    """
    levels = {
        0: 'INFO ',
        1: 'OK   ',
        2: 'WARN ',
        3: 'ERROR',
        4: 'FATAL'
    }
    if not args.verbose and not i:
        if l < 3:
            return
    print('[%.3f' % (time.time() - d_time) + '] ' + '[' + levels[l] + ']', s)


graph_width = 220
graph_height = 220
grid_spacing_y = 30
grid_spacing_x = 30
graph_x_offset = 48
graph_y_offset = 20
point_size = 1.5
messages_received = 0


def count_online():
    """
    Counts counts online sensors.

    :return: number of sensors found in register
    """
    i = 0
    for sensor in sensors:
        if sensor.is_active:
            i += 1
    return i


class Measurement:
    def __init__(self, ts, t, l, s, p, h):
        self.timestamp = ts
        self.temp = float(t)
        self.light = int(l)
        self.sound = int(s)
        self.pressure = float(p)
        self.humidity = int(h)

    def __getitem__(self, item):
        return [self.timestamp, self.temp, self.light, self.sound, self.pressure, self.humidity][item]


class Sensor:
    """
    Object to handle individual sensor modules.

    :param addr: IP address of the sensor
    :param port: Port of the sensor
    :param name: Name of the board
    :return: Sensor object
    """

    def __init__(self, addr, port, name, colour):
        self.name = name
        self.colour = colour
        self.thread = threading.Thread(target=self.read)
        self.address = addr
        self.port = port
        self.measurements = []
        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter())
        self.is_active = False
        self.combined_address = self.address + ':' + str(self.port)
        debug("Created sensor " + self.name + " at " + self.combined_address, 1)

    def read(self):
        """
        Read data from the sensor into Measurement objects

        :return: Decoded data.
        """
        try:
            r = self.session.get('http://' + self.address + ':' + str(self.port))  # Thank god for requests
        except requests.exceptions.ConnectionError:
            return
        if len(r.content.decode().split()) != 5:
            debug(
                "Invalid data sent by board " +
                self.name + " at " + self.combined_address +
                ", probably a network error",
                3)
            return
        else:
            self.measurements.append(Measurement(hex(int(datetime.now().timestamp())), *r.content.decode().split()))
            global messages_received  # I apologise
            messages_received += 1
            self.is_active = True
        with open('sensorlogs/' + self.name + '.csv', 'a') as file:
            file.write(','.join((str(hex(int(datetime.now().timestamp())) + ' ' + r.content.decode()).split())) + '\n')
        debug("Received and logged valid data from " + self.name + " at " + self.combined_address)
        return r.content.decode()

    def start_thread(self):
        """
        Starts the read process in a separate thread.
        """
        self.thread = threading.Thread(target=self.read)
        self.thread.start()
        root.after(150, self.start_thread)

    def __str__(self):
        return self.name


class GraphFrame:
    def __init__(self, root, x, y, dx, dy, t, increment, m_index, max_measurements):
        self.max_measurements = max_measurements
        self.increment = increment
        self.m_index = m_index
        self.graph_width = graph_width * dx + 4 * (dx - 1)
        self.graph_height = graph_height * dy + 4 * (dy - 1)
        self.frame = Frame(root)
        self.title = Label(self.frame, text=t)
        self.frame.grid(column=x, row=y, columnspan=dx, rowspan=dy, sticky='nsew')
        self.frame.columnconfigure(x, weight=1)
        self.frame.rowconfigure(y, weight=1)
        self.text = t
        self.graph = Canvas(self.frame, width=self.graph_width, height=self.graph_height, bg='black')
        self.graph.grid(row=0)
        debug("Created graph frame at (%s, %s)" % (x, y))

    def update(self):
        self.graph.delete(ALL)
        y = 0
        self.graph.create_text(self.graph_width // 2, 15, text=self.text, font=('Courier New', 10), fill="#FFFFFF")
        i = 0
        for y in range(graph_height - graph_y_offset, graph_y_offset, -grid_spacing_y):
            self.graph.create_line(graph_x_offset, y, graph_x_offset - 5, y, fill="blue")
            self.graph.create_text(graph_x_offset - 10, y, text=str(i), font=('Courier New', 10), fill='#00FF00',
                                   anchor=E)
            i += self.increment
        self.graph.create_line(
            graph_x_offset,
            graph_height - graph_y_offset,
            graph_x_offset,
            y,
            fill="blue"
        )
        for sensor in sensors:
            i = graph_x_offset
            m_list = []
            for measurement in sensor.measurements[-self.max_measurements:] if \
                            len(sensor.measurements) > self.max_measurements else sensor.measurements:
                self.add_point(i, self.get_grid_y(measurement[self.m_index]))
                m_list.append((i, measurement[self.m_index]))
                i += 50
            self.draw_lines(m_list, sensor.colour)
        root.after(50, self.update)

    def add_point(self, x, y):
        self.graph.create_oval(
            x - point_size,
            y - point_size,
            x + point_size,
            y + point_size,
            fill="#FFFFFF",
            outline="#FFFFFF",
        )

    def draw_lines(self, l, colour):
        i = 1
        for p in l[1:]:
            t = (
                p[0],
                self.get_grid_y(p[1]),
                l[i - 1][0],
                self.get_grid_y(l[i - 1][1])
            )
            self.graph.create_line(t, fill=colour)
            i += 1

    def get_grid_y(self, y):
        return (graph_height - graph_y_offset) - (y / self.increment) * grid_spacing_y


class InfoFrame:
    def __init__(self, root, x, y, dx, dy, t):
        self.graph_width = graph_width * dx
        self.graph_height = graph_height * dy
        self.frame = Frame(root)
        self.title = Label(self.frame, text=t)
        self.frame.grid(column=x, row=y, columnspan=dx, rowspan=dy, sticky='nsew')
        self.frame.columnconfigure(x, weight=1)
        self.frame.rowconfigure(y, weight=1)
        self.text = t
        self.graph = Canvas(self.frame, width=graph_width * dx, height=graph_height * dy, bg='black')
        self.graph.grid(row=0)

    def update(self):
        self.graph.delete(ALL)
        self.graph.create_text(
            self.graph_width // 2, 15,
            text=str(count_online()) + '/' + str(len(sensors)) + " sensors online",
            font=('Courier New', 10),
            fill="#FFFFFF"
        )
        i = 30
        for sensor in sensors:
            self.graph.create_text(self.graph_width // 2, i, text=sensor.name, font=('Courier New', 10),
                                   fill=sensor.colour if sensor.is_active else "#999999")
            i += 15
        self.graph.create_text(
            self.graph_width // 2, i,
            text="Messages received: " + str(messages_received),
            font=('Courier New', 10),
            fill="#FFFFFF"
        )
        i += 15
        self.graph.create_text(
            self.graph_width // 2, i,
            text="Start time: " + start_time.isoformat().split('T')[1].split('.')[0],
            font=('Courier New', 10),
            fill="#FFFFFF"
        )
        root.after(50, self.update)


if __name__ == '__main__':
    stime = time.time()

    parser = argparse.ArgumentParser(description="Monitoring GUI for sensorboards.")
    parser.add_argument('-v', '--verbose', help='turn on verbose output mode (for debugging)', action='store_true')
    args = parser.parse_args()

    root = Tk()

    root.resizable(0, 0)
    debug("Created window object", 1, True)
    start_time = datetime.now()
    debug("Start time: " + ' '.join(start_time.isoformat().split("T")), 0, True)
    sensors = [
        # Sensor("192.168.0.6", 80, "Celaeno", "#FF5555"),
        Sensor("192.168.0.15", 80, "Alcyone", "#55FF55"),
        # Sensor("192.168.0.19", 80, "Maia", "#5555FF"),
        # Sensor("192.168.0.20", 80, "Atlas", "#FFFF55"),
    ]
    debug("Created all sensor objects", 1, True)
    temp_frame = GraphFrame(root, 0, 0, 2, 1, "Temperature", 10, 1, 8)
    light_frame = GraphFrame(root, 0, 1, 1, 1, "Light", 200, 2, 4)
    sound_frame = GraphFrame(root, 2, 0, 2, 1, "Sound", 200, 3, 8)
    pressure_frame = GraphFrame(root, 1, 1, 1, 1, "Pressure", 100, 4, 4)
    humidity_frame = GraphFrame(root, 2, 1, 1, 1, "Humidity", 400, 5, 4)
    info_frame = InfoFrame(root, 3, 1, 1, 1, "Info")

    temp_frame.update()
    sound_frame.update()
    light_frame.update()
    pressure_frame.update()
    humidity_frame.update()
    info_frame.update()
    debug("Initial frame update complete", 1, True)
    for sensor in sensors:
        sensor.start_thread()

    root.mainloop()
