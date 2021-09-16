#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import serialConnector
from threading import Thread

class SerialClass:

    def __init__(self):
        # port = '/dev/ttyACM1'
        port = '/dev/ttyACM0'
        rate = 115200
        self.ser = serialConnector.Serial(
            port=port,
            baudrate=rate,
            bytesize=serialConnector.EIGHTBITS,
            stopbits=serialConnector.STOPBITS_ONE
        )
        print("Connection to serial port established.")

    def serial_start(self):
        Thread(target=self.write_speeds, args=()).start()

    def write_speeds(self, speedstr):
        self.ser.write(speedstr.encode('utf-8'))

