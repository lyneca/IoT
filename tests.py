import gui

gui.args.verbose = True
gui.args.debug = True
# Creates a sensor at ip:port
gui.debug("Creating test sensor", -1)
ip = "192.168.0.15"
port = 80
test_sensor = gui.Sensor(ip, port, "TestSensor", "#55FF55")

# Grab some data from the sensor - if this works, the sensor will flash orange, then briefly blue.
gui.debug("Reading data from test sensor.", -1)
gui.debug("Sensor should flash orange, then briefly blue.", -1)
content = test_sensor.read()
gui.debug("Received data:", -1)
gui.debug(content, -1)
