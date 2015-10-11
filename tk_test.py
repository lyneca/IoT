__author__ = 'wing2048'
from tkinter import *
import threading

import serial


port = 'COM4'

point_size = 1.5
graph_x_offset = 48
graph_y_offset = 32

graph_width = 300
graph_height = 300

grid_spacing_y = 23
grid_spacing_x = 30

signal_delay = 100
time_magnitude = 100
root = Tk()
root.wm_title('Readings from Arduino on ' + port)
root.configure(background='black')
t_graph = Canvas(root, width=graph_width, height=graph_height, bg='black')
l_graph = Canvas(root, width=graph_width, height=graph_height, bg='black')
s_graph = Canvas(root, width=graph_width, height=graph_height, bg='black')
t_graph.grid(row=0, column=0)
l_graph.grid(row=1, column=0)
s_graph.grid(row=0, column=1)


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
    c.create_text(graph_width // 2, 20, text=title, font=('Courier New', 10), fill="#FFFFFF")
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
        graph_width // 2,
        graph_height - 10,
        text='%s Seconds' % (t_start / 10),
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
    temp_list = []
    while True:
        read = s.read()
        if read == b'\r':
            break
        temp_list.append(read.decode())
    m_list.append(Measurement(*''.join(temp_list).strip().split()))
    with open('data.db', 'a') as file:
        file.write(''.join(temp_list).strip() + '\n')
    t_points = []
    l_points = []
    s_points = []
    for m in m_list:
        l_points.append(map(m.light, 0, 1000, 0, graph_height / grid_spacing_y - 3))
        t_points.append(map(m.temp, 0, 45, 0, graph_height / grid_spacing_y - 3))
        s_points.append(map(m.sound, 0, 100, 0, graph_height / grid_spacing_y - 3))
        if len(t_points) > graph_width / grid_spacing_x - 1:
            t_points.pop(0)
        if len(l_points) > graph_width / grid_spacing_x - 1:
            l_points.pop(0)
        if len(s_points) > graph_width / grid_spacing_x - 1:
            s_points.pop(0)
    redraw(t_graph, t_points, 5, len(m_list), 'Temperature (Degrees Celsius)')
    redraw(l_graph, l_points, 100, len(m_list), 'Light Level (Possibly Lux?)')
    redraw(s_graph, s_points, 10, len(m_list), 'Sound level (Decibels)')
    root.after(1, start_update_thread)


m_list = []
s = serial.Serial(port, 9600)
root.after(1, start_update_thread)
root.mainloop()