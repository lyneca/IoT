import math

__author__ = 'wing2048'
from tkinter import *
import threading
import random
import socket

import serial


debug = False
fake_data = False

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
# action_bar = Frame(root)


class VerticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)
        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth(), height=frame_height * 2)

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)

        return


root_frame = VerticalScrolledFrame(root, height=frame_height * 2)
root_frame.interior.configure(height=frame_height * 4)
root_frame.pack()


class Sensor:
    def __init__(self, x, y, address, port, t='', dummy=fake_data, is_serial=False):
        y += 1
        self.is_serial = is_serial
        self.frame = Frame(root_frame.interior, width=frame_width, height=frame_height)
        self.frame.grid(column=x, row=y, sticky='nsew')
        self.temp = Canvas(self.frame, width=graph_width * 2 + 4, height=graph_height, bg='black')
        self.light = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        self.sound = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        self.humid = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        self.press = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        # self.overview = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        self.title = Label(self.frame, text=t)
        self.title.grid(row=0, columnspan=2, sticky='nsew')
        self.light.grid(row=1, column=0, sticky='nsew')
        self.sound.grid(row=1, column=1, sticky='nsew')
        self.temp.grid(row=2, columnspan=2, sticky='nsew')
        self.humid.grid(row=3, column=0, sticky='nsew')
        self.press.grid(row=3, column=1, sticky='nsew')

        # self.overview.grid(row=2, column=1)

        self.is_dummy = dummy

        self.port = port
        self.address = address

        self.m_list = []
        self.t_points = []
        self.l_points = []
        self.s_points = []
        self.h_points = []
        self.p_points = []
        if not dummy:
            if self.is_serial:
                self.serial = serial.Serial(self.port, 9600)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = threading.Thread(target=self.read)

    def read(self):
        temp_list = []
        if self.is_dummy:
            self.m_list.append(Measurement(
                1,
                random.randint(300, 400),
                random.randint(15, 20),
                random.randint(250, 350),
                random.randint(10, 20),
                random.randint(1000, 1500),
            ))
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
        self.h_points = []
        self.p_points = []
        for m in self.m_list:
            self.l_points.append(map(m.light, 0, 1000, 0, graph_height / grid_spacing_y - 3))
            self.t_points.append(map(m.temp, 0, 45, 0, graph_height / grid_spacing_y - 3))
            self.s_points.append(map(m.sound, 0, 600, 0, graph_height / grid_spacing_y - 3))
            self.h_points.append(map(m.humid, 0, 2000, 0, graph_height / grid_spacing_y - 3))
            self.p_points.append(map(m.press, 0, 2000, 0, graph_height / grid_spacing_y - 3))
            if len(self.t_points) > graph_width * 2 / grid_spacing_x - 1:
                self.t_points.pop(0)
            if len(self.l_points) > graph_width / grid_spacing_x - 1:
                self.l_points.pop(0)
            if len(self.s_points) > graph_width / grid_spacing_x - 1:
                self.s_points.pop(0)
            if len(self.h_points) > graph_width / grid_spacing_x - 1:
                self.h_points.pop(0)
            if len(self.p_points) > graph_width / grid_spacing_x - 1:
                self.p_points.pop(0)
        root.after(1000, self.start_thread)


    def start_thread(self):
        self.thread = threading.Thread(target=self.read)
        self.thread.start()


class InfoFrame():
    def __init__(self, root, x, y, dx, dy, t):
        self.frame = Frame(root)
        self.spacer = Label(self.frame)
        self.title = Label(self.frame, text=t)
        self.frame.grid(column=x, row=y, columnspan=dx, rowspan=dy, sticky='nsew')
        self.frame.columnconfigure(x, weight=1)
        self.frame.rowconfigure(y, weight=1)
        self.title.grid(row=0)
        self.spacer.grid(row=3)


class CompareGraph():
    def __init__(self, r, x, y, t, type):
        self.type = type
        self.frame = Frame(r)
        # self.label = Label(self.frame, text=t)
        self.graph = Canvas(self.frame, width=graph_width, height=graph_height, bg='black')
        # self.label.grid(column=0, row=0)
        self.graph.grid(column=0, row=1)
        self.frame.grid(column=x, row=y)
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
        self.graph.create_text(
            graph_width // 2,
            16,
            text=self.text,
            font=('Courier New', 10),
            fill="#FFFFFF"
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
                elif self.type == 4:
                    point = map(sensor.m_list[-1].humid, 0, 2000, 0, graph_height - 32)
                elif self.type == 5:
                    point = map(sensor.m_list[-1].press, 0, 2000, 0, graph_height - 32)
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

# Home 10.2.1.57
# School 10.26.141.192
sensors = [
    Sensor(0, 1, "10.2.1.57", 8080, "1: Alcyone"),
    Sensor(1, 1, "0.0.0.0", 8080, "2: Atlas"),
    Sensor(2, 1, "0.0.0.0", 8080, "3: Asterope"),
    Sensor(0, 2, "0.0.0.0", 8080, "4: Celaeno"),
    Sensor(1, 2, "0.0.0.0", 8080, "5: Maia"),
    Sensor(2, 2, "0.0.0.0", 8080, "6: Taygeta"),
]

# info_frame = InfoFrame(root_frame.interior, 0, 3, 2, 2, '')
compare_frame_1 = Frame(root_frame.interior)
compare_frame_2 = Frame(root_frame.interior)
compare_frame_3 = Frame(root_frame.interior)
compare_frame_1.grid(column=0, row=0)
compare_frame_2.grid(column=1, row=0)
compare_frame_3.grid(column=2, row=0)
temp_compare = CompareGraph(compare_frame_1, 0, 0, "Temperature", 1)
sound_compare = CompareGraph(compare_frame_1, 1, 0, "Sound", 3)
light_compare = CompareGraph(compare_frame_2, 0, 0, "Light", 2)
humid_compare = CompareGraph(compare_frame_2, 1, 0, "Humidity", 4)
press_compare = CompareGraph(compare_frame_3, 0, 0, "Pressure", 5)
place_compare = CompareGraph(compare_frame_3, 1, 0, "", 0)


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
    def __init__(self, t, l, c, s, p, h):
        self.time = int(t) / 1000
        self.temp = float(c)
        self.light = int(l)
        self.sound = float(s)
        self.press = float(p)
        self.humid = float(h)


def start_update_thread():
    update_thread = threading.Thread(target=update)
    update_thread.start()


def update():
    temp_compare.update()
    light_compare.update()
    sound_compare.update()
    humid_compare.update()
    press_compare.update()

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
            'Light: ' + (str(sensor.m_list[-1].light) if len(sensor.m_list) > 0 else '0')
        )
        redraw(
            sensor.sound,
            sensor.s_points,
            20,
            len(sensor.m_list),
            'Sound: ' + (str(sensor.m_list[-1].sound) if len(sensor.m_list) > 0 else '0')
        )
        redraw(
            sensor.humid,
            sensor.h_points,
            20,
            len(sensor.m_list),
            'Humidity: ' + (str(sensor.m_list[-1].humid) if len(sensor.m_list) > 0 else '0')
        )
        redraw(
            sensor.press,
            sensor.p_points,
            2000 // (graph_height // grid_spacing_y),
            len(sensor.m_list),
            'Pressure: ' + (str(sensor.m_list[-1].press) if len(sensor.m_list) > 0 else '0')
        )
        # draw_overview(
        # sensor
        # )
    root.after(1000, start_update_thread)


for sensor in sensors:
    if not sensor.thread.is_alive():
        sensor.start_thread()
        # sensor.start_update()
root.after(1, start_update_thread)
root.resizable(0, 0)
root.mainloop()