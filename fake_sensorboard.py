import http.server as http_server
import random


def get_http_response(data):
    header = b"""
    HTTP/1.0 200 OK
    Content-Type: text/html
    Content-Length: %s

    %s
    """ % (str(len(data)).encode(), data)
    return header


def get_fake_data():
    data = [
        random.randint(10, 40) + round(random.random(), 2),
        random.randint(50, 300),
        random.randint(200, 700),
        random.randint(99, 102) + round(random.random(), 2),
        random.randint(400, 600)
    ]
    return ' '.join([str(x) for x in data]).encode()


class SensorRequestHandler(http_server.BaseHTTPRequestHandler):
    def do_GET(self):
        print("Got request from %s:" % (self.client_address[0]))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(get_fake_data())

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


from socket import *

sock = socket()
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

print("Starting server...")
http_server.HTTPServer.allow_reuse_address = True
server = http_server.HTTPServer(("localhost", 80), SensorRequestHandler)
print("Server up.")
server.serve_forever()
