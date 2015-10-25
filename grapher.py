__author__ = 'wing2048'
from tkinter import *
import threading
import random
import socket

import serial


debug = True
fake_data = True

point_size = 1.5
graph_x_offset = 48
graph_y_offset = 32

frame_width = 300
frame_height = 300

graph_width = frame_width // 2
graph_height = frame_height // 2

grid_spacing_y = 23
grid_spacing_x = 30

signal_delay = 100
time_magnitude = 100
root = Tk()
root.wm_title('Readings from sensors')
root.configure(background='black')
action_bar = Frame(root)


class Sensor:
    def __init__(self, x, y, address, port, t='', dummy=fake_data, is_serial=False):
        y += 1
        self.is_serial = is_serial
        self.frame = Frame(root, width=frame_width, height=frame_height)
        self.frame.grid(column=x, row=y)
        self.temp = Canvas(self.frame, width=graph_width * 2 + 4, height=graph_height, bg='black')
        self.light = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        self.sound = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        self.title = Label(self.frame, text=t)
        self.title.grid(row=0, columnspan=2)
        self.light.grid(row=1, column=0)
        self.sound.grid(row=1, column=1)
        self.temp.grid(row=2, columnspan=2)

        self.is_dummy = dummy

        self.port = port
        self.address = address

        self.m_list = []
        self.t_points = []
        self.l_points = []
        self.s_points = []
        if not dummy:
            if self.is_serial:
                self.serial = serial.Serial(self.port, 9600)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = threading.Thread(target=self.read)

    def read(self):
        temp_list = []
        if self.is_dummy:
            self.m_list.append(Measurement(1, random.randint(300, 400), random.randint(15, 20), random.randint(30, 60)))
        else:
            if self.is_serial:
                while True:
                    read = self.serial.read()
                    if read == b'\r':
                        break
                    temp_list.append(read.decode())
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.address, self.port))
                recvd = self.socket.recv(100)
                temp_list.append(recvd.decode())
            self.m_list.append(Measurement(*''.join(temp_list).strip().split()))
        self.t_points = []
        self.l_points = []
        self.s_points = []
        for m in self.m_list:
            self.l_points.append(map(m.light, 0, 1000, 0, graph_height / grid_spacing_y - 3))
            self.t_points.append(map(m.temp, 0, 45, 0, graph_height / grid_spacing_y - 3))
            self.s_points.append(map(m.sound, 0, 600, 0, graph_height / grid_spacing_y - 3))
            if len(self.t_points) > graph_width * 2 / grid_spacing_x - 1:
                self.t_points.pop(0)
            if len(self.l_points) > graph_width / grid_spacing_x - 1:
                self.l_points.pop(0)
            if len(self.s_points) > graph_width / grid_spacing_x - 1:
                self.s_points.pop(0)
        root.after(1000, self.start_thread)

    def start_thread(self):
        self.thread = threading.Thread(target=self.read)
        self.thread.start()


sensors = [
    Sensor(0, 0, "10.2.1.57", 8080, "Alcyone", False),
    Sensor(1, 0, "10.2.1.57", 8080, "Atlas"),
    Sensor(2, 0, "10.2.1.57", 8080, "Asterope"),
    Sensor(0, 1, "10.2.1.57", 8080, "Celaeno"),
    Sensor(1, 1, "10.2.1.57", 8080, "Maia"),
    Sensor(2, 1, "10.2.1.57", 8080, "Taygeta"),
]

action_bar.grid(column=0, row=0, columnspan=root.grid_size()[0])


def map(v, fl, fh, tl, th):
    return (v - fl) / (fh - fl) * (th - tl) + tl


def add_point(c, x, y):
    c.create_oval(
        x * grid_spacing_x + graph_x_offset - point_size,
        (graph_height - graph_y_offset) - (y * grid_spacing_y - point_size),
        x * grid_spacing_x + graph_x_offset + point_size,
        (graph_height - graph_y_offset) - (y * grid_spacing_y + point_size),
        fill="red",
        outline="red"
    )


def get_grid(l):
    return (graph_height - graph_y_offset) - l * grid_spacing_y


def redraw(c, point_list, inc_val, t_start, title):
    c.delete(ALL)
    y = 0
    c.create_text(c.winfo_width() // 2, 20, text=title, font=('Courier New', 10), fill="#FFFFFF")
    i = 0
    for y in range(graph_height - graph_y_offset, graph_y_offset, -grid_spacing_y):
        c.create_line(graph_x_offset, y, graph_x_offset - 5, y, fill="blue")
        c.create_text(graph_x_offset - 10, y, text=i, font=('Courier New', 10), fill='#00FF00', anchor=E)
        i += inc_val
    c.create_line(
        graph_x_offset,
        graph_height - graph_y_offset,
        graph_x_offset,
        y,
        fill="blue"
    )
    c.create_text(
        c.winfo_width() // 2,
        graph_height - 10,
        text='%s Measurements' % t_start,
        font=('Courier New', 10),
        fill="#FFFFFF"
    )
    i = 0
    for point in point_list:
        add_point(c, i, point)
        i += 1
    draw_lines(point_list, c)


def draw_lines(l, c):
    i = 1
    for p in l[1:]:
        t = (
            i * grid_spacing_x + graph_x_offset,
            get_grid(p),
            (i - 1) * grid_spacing_x + graph_x_offset,
            get_grid(l[i - 1])
        )
        c.create_line(t, fill='#00FF00')
        i += 1


class Measurement():
    def __init__(self, t, l, c, s):
        self.time = int(t) / 1000
        self.temp = float(c)
        self.light = int(l)
        self.sound = float(s)


def start_update_thread():
    update_thread = threading.Thread(target=update)
    update_thread.start()


def update():
    for sensor in sensors:
        redraw(
            sensor.temp,
            sensor.t_points,
            10,
            len(sensor.m_list),
            'Temperature'
        )
        redraw(
            sensor.light,
            sensor.l_points,
            1000 // (graph_height // grid_spacing_y),
            len(sensor.m_list),
            'Light Level'
        )
        redraw(
            sensor.sound,
            sensor.s_points,
            10,
            len(sensor.m_list),
            'Sound level'
        )
    root.after(1000, start_update_thread)


for sensor in sensors:
    if not sensor.thread.is_alive():
        sensor.start_thread()
root.after(1, start_update_thread)
root.mainloop()