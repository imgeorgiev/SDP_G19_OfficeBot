# Reads data off the serial bus and splits it into
# returns data in format [LR, RR, LF, RF]

import serial


class IR_Bus():
	def __init__(self, port = '/dev/ttyACM1', baud = 9600):
		self.IR_LR = 0
		self.IR_RR = 0
		self.IR_LF = 0
		self.IR_RF = 0
		serial_str = ""
		# TODO: error checking for port
		ser = serial.Serial(port,baud)
	def read():
		serial_str = str(ser.readline())
		serial_str = serial_str.split(",")
		return serial_str

