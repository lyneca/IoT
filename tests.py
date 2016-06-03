import gui

# Creates a sensor at ip:port
ip = "192.168.0.15"
port = 80
test_sensor = gui.Sensor(ip, port, "TestSensor", "#55FF55")

# Grab some data from the sensor - if this works, the sensor will flash orange, then briefly blue.
content = test_sensor.read()
print(content)
