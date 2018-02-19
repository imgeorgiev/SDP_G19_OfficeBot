#!/usr/bin/env python3


# Library for sending UDP commands to an EV3
# Commands include: motors

import socket
import sys


tcp_ip = "169.254.21.44"
tcp_port = 5005
tcp_message = "test1"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('DEBUG: Socket created')


def clientthread(conn):
    # Sending message to connected client
    conn.send('Welcome to the server. Receving Data...\n')

    # infinite loop so that function do not terminate and thread do not end.
    while True:

        # Receiving from client
        data = conn.recv(1024)
        reply = 'Message Received at the server!\n'
        print(data)
        if not data:
            break

        conn.sendall(reply)

    conn.close()


def main():
    try:
        sock.bind((tcp_ip, tcp_port))
    except (socket.error, msg):
        print('DEUBG: Bind failed. Error Code : ' + str(msg[0]) + ' Message ' +
            msg[1])
        sys.exit()

    sock.listen(10)
    print('DEBUG: Socket now listening')

    # now keep talking with the client
    while 1:
        # wait to accept a connection
        conn, addr = sock.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        clientthread(conn)

    sock.close()


if __name__ == '__main__':
    main()