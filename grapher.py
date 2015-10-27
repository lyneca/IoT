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
    def __init__(self, root, x, y, address, port, t='', dummy=fake_data, is_serial=False):
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
            self.m_list.append(Measurement(1, random.randint(300, 400), random.randint(15, 20), random.randint(250, 350)))
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

    def start_update(self):
        thread = threading.Thread(target=self.update())
        thread.start()

    def update(self):
        root.after(1, self.start_update)

    def start_thread(self):
        self.thread = threading.Thread(target=self.read)
        self.thread.start()


class InfoFrame():
    def __init__(self, root, x, y, dx, dy, t):
        self.frame = Frame(root)
        self.spacer = Label(self.frame, text='Compare Data')
        self.title = Label(self.frame, text='WiFi Signal')
        self.frame.grid(column=x, row=y, columnspan=dx, rowspan=dy)
        self.title.grid(row=0)
        self.spacer.grid(row=2)


class CompareGraph():
    def __init__(self, r, y, t, type):
        self.type = type
        self.frame = Frame(r)
        # self.label = Label(self.frame, text=t)
        self.graph = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        # self.label.grid(column=0, row=0)
        self.graph.grid(column=0, row=1)
        self.frame.grid(row=y)
        self.text = t

    def update(self):
        self.graph.delete(ALL)
        self.graph.create_line(
            16,
            graph_height - 16,
            graph_width - 16,
            graph_height - 16,
            fill='blue'
        )
        i = 0
        for sensor in sensors:
            point = 0
            if len(sensor.m_list) > 0:
                if self.type == 0:
                    # point = sensor.t_points[-1]
                    pass
                elif self.type == 1:
                    point = map(sensor.m_list[-1].temp, 0, 45, 0, graph_height - 32)
                elif self.type == 2:
                    point = map(sensor.m_list[-1].light, 0, 1000, 0, graph_height - 32)
                elif self.type == 3:
                    point = map(sensor.m_list[-1].sound, 0, 600, 0, graph_height - 32)
            self.graph.create_text(
                graph_width // 2,
                16,
                text=self.text,
                font=('Courier New', 10),
                fill="#FFFFFF"
            )
            self.graph.create_text(
                16 + i * ((graph_width - 32) / len(sensors)) + ((graph_width - 32) / len(sensors)) // 2,
                graph_height - 8,
                text=str(i),
                font=('Courier New', 10),
                fill="#00FF00"
            )
            self.graph.create_rectangle(
                16 + i * ((graph_width - 32) / len(sensors)),
                graph_height - 16,
                16 + i * ((graph_width - 32) / len(sensors)) + ((graph_width - 32) / len(sensors)),
                graph_height - 16 - point,
                fill="#003300",
                outline="#00FF00"
            )
            i += 1


info_frame = InfoFrame(root, 3, 1, 1, 2, 'Compare')
wifi_compare = CompareGraph(info_frame.frame, 1, "WiFi", 0)
temp_compare = CompareGraph(info_frame.frame, 3, "Temperature", 1)
light_compare = CompareGraph(info_frame.frame, 4, "Light", 2)
sound_compare = CompareGraph(info_frame.frame, 5, "Sound", 3)

# Home 10.2.1.57
# School 10.26.141.192

sensors = [
    Sensor(root, 0, 0, "10.26.141.192", 8080, "1: Alcyone"),
    Sensor(root, 1, 0, "10.2.1.57", 8080, "2: Atlas"),
    Sensor(root, 2, 0, "10.2.1.57", 8080, "3: Asterope"),
    Sensor(root, 0, 1, "10.2.1.57", 8080, "4: Celaeno"),
    Sensor(root, 1, 1, "10.2.1.57", 8080, "5: Maia"),
    Sensor(root, 2, 1, "10.2.1.57", 8080, "6: Taygeta"),
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
        outline="red",
        tags='point'
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
    wifi_compare.update()
    temp_compare.update()
    light_compare.update()
    sound_compare.update()

    for sensor in sensors:
        redraw(
            sensor.temp,
            sensor.t_points,
            10,
            len(sensor.m_list),
            'Temperature: ' + (str(sensor.m_list[-1].temp) if len(sensor.m_list) > 0 else '0')
        )
        redraw(
            sensor.light,
            sensor.l_points,
            1000 // (graph_height // grid_spacing_y),
            len(sensor.m_list),
            'Light Level: ' + (str(sensor.m_list[-1].light) if len(sensor.m_list) > 0 else '0')
        )
        redraw(
            sensor.sound,
            sensor.s_points,
            20,
            len(sensor.m_list),
            'Sound level: ' + (str(sensor.m_list[-1].sound) if len(sensor.m_list) > 0 else '0')
        )
    root.after(1000, start_update_thread)


for sensor in sensors:
    if not sensor.thread.is_alive():
        sensor.start_thread()
root.after(1, start_update_thread)
root.mainloop()