#!/usr/bin/env python3


# Library for receiving UDP commands to an EV3
# Commands include: motors

import socket


udp_ip = "169.254.21.44"
udp_port = 5005
udp_message = "test1"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message:" + str(data))
