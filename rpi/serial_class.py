#!/usr/bin/env python3

# Reads data off the serial bus and splits it into
# returns data in format [LR, RR, LF, RF]

import serial


class IR_Bus():
    IR_LR = 0
    IR_RR = 0
    IR_LF = 0
    IR_RF = 0
    ser = serial.Serial()

    def __init__(self, port='/dev/ttyACM0', baud=9600):
        self.IR_LR = 0
        self.IR_RR = 0
        self.IR_LF = 0
        self.IR_RF = 0
        # TODO: error checking for port
        print(port)
        self.ser = serial.Serial(port, baud)

    def read(self):
        serial_str = str(self.ser.readline())[2:-6]
        serial_str = serial_str.split(",")

        if(len(serial_str) == 4):
            self.IR_LR = serial_str[0]
            self.IR_RR = serial_str[1]
            self.IR_LF = serial_str[2]
            self.IR_RF = serial_str[3]
            return serial_str


def main():
    print("Starting serial read")
    IR = IR_Bus()
    print("Connected to {0} at {1} baudrate".format(IR.ser.port,
        IR.ser.baudrate))
    while(True):
        print("Serial string" + str(IR.read()))
        print("IR_LR = " + str(IR.IR_LR))
        print("IR_RR = " + str(IR.IR_RR))
        print("IR_LF = " + str(IR.IR_LF))
        print("IR_RF = " + str(IR.IR_RF))


if __name__ == '__main__':
    main()
