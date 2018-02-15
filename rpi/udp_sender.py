#!/usr/bin/env python3


# Library for sending UDP commands to an EV3
# Commands include: motors

import socket


udp_ip = "169.254.21.44"
udp_port = 5005
udp_message = "test1"


while(True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(bytes(udp_message, "utf-8"), (udp_ip, udp_port))
