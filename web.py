################################################################################
# Web Interface
################################################################################

################################################################################
# IMPORTS
################################################################################
import time
import zmq
import socket
import struct
import threading
import json
import os

################################################################################
# CLASSES
################################################################################


################################################################################
# VARIABLES
################################################################################
context = None

current_temp = 999.0
cooling = 0
heating = 0
alarm = 0
platform = "Ubuntu"

setpoint = 0.0

################################################################################
# FUNCTIONS
################################################################################

def worker():
    """
        Thread to communicate with the management interface
    """
    global context
    global setpoint

    management_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    management_socket.bind(("0.0.0.0", 6665))

    tc_pub_socket = context.socket(zmq.PUB)
    tc_pub_socket.connect("ipc:///tmp/feeds/1")

    while True:
        message, addr = management_socket.recvfrom(128)

        print "WEB: interface ", addr

        #Decode flatbuffer

        #Publish settings for TC
        tc_pub_socket.send(json.dumps({"setpoint": setpoint}))

        #Because of hiccup with the serializer in the seL4 world, this is necesarry for now
        reply = struct.pack("fiii16s", current_temp, cooling, heating, alarm, platform)

        #management_socket.connect(addr)
        management_socket.sendto(reply, (addr[0], 6666))



################################################################################
# MAIN
################################################################################

def main():
    global context
    global current_temp

    if not os.path.exists("/tmp/feeds"):
        os.makedirs("/tmp/feeds")

    context = zmq.Context()
    tc_socket = context.socket(zmq.SUB)
    tc_socket.setsockopt(zmq.SUBSCRIBE, "")
    tc_socket.bind("ipc:///tmp/feeds/0") 

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    while True:
        #  Wait for next request from client
        message = tc_socket.recv()
        print "WEB: tc", message
        message = json.loads(message)
        current_temp = message["currentTemp"] 

if __name__ == "__main__":
    main()
