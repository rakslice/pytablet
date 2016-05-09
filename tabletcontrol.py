import sys

import time

from control_interface import ControlInterface

import serial


def read_to_cr(ser):
    out = []
    while True:
        ch = ser.read(1)
        if ch == "\r":
            break
        out.append(ch)
    return "".join(out)


def ser_cmd_w_response(ser, cmd):
    ser.write(cmd + "\r")
    ser.read(len(cmd))
    return read_to_cr(ser)


def ser_cmd(ser, cmd):
    ser.write(cmd + "\r")


def hex_repr(data):
    parts = ["%02x" % ord(c) for c in data]
    return ":".join(parts)


class ProcessTabletSerialCommands(object):
    def __init__(self, serial_port_device_name, control_interface):
        assert isinstance(control_interface, ControlInterface)
        self.control_interface = control_interface
        self.serial_port_device_name = serial_port_device_name
        self.running = False

    def log(self, msg):
        print >> sys.stderr, msg

    def run(self):
        self.running = True

        # https://pythonhosted.org/pyserial/shortintro.html#opening-serial-ports
        baudrate = 9600

        self.log("Opening serial port %r at %r" % (self.serial_port_device_name, baudrate))
        ser = serial.Serial()
        # self.serial_port_device_name)  # open serial port
        ser.baudrate = baudrate
        ser.port = self.serial_port_device_name
        ser.open()
        try:

            # protocol description:
            # http://linuxwacom.sourceforge.net/wiki/index.php/Serial_Protocol_IV

            # check which port was really used
            self.log("Serial port %r opened" % ser.name)
            print(ser.name)

            # query model
            ser.write("~#")
            ser.read(2)

            model = read_to_cr(ser)
            print model

            # iv
            # ser_cmd(ser, "\r#")

            config_string = ser_cmd_w_response(ser, "~R")
            print "Config string: %r" % config_string

            max_coordinates = ser_cmd_w_response(ser, "~C")
            print "Max coordinates: %r" % max_coordinates
            max_x, max_y = [int(v) for v in max_coordinates.split(",")]

            # max rate

            # in principle this command is supposed to bump us up to a faster rate; not sure if it works
            ser_cmd(ser, "IT0")

            # time.sleep(0.125)

            # print "closing"
            # ser.close()
            # ser = serial.Serial()
            # ser.baudrate = 19200
            # ser.port = self.serial_port_device_name
            # print "reopening"
            # ser.open()

            # time.sleep(0.125)
            # print "doing config again"
            #
            # ser.write("~#")
            # ser.read(2)
            #
            # model = read_to_cr(ser)
            # print model
            #
            # config_string = ser_cmd_w_response(ser, "~R")
            # print "Config string: %r" % config_string
            #

            # pressure mode
            self.log("Enabling pressure mode")
            ser_cmd(ser, "PH1")

            self.log("Disabling incremental mode")
            ser_cmd(ser, "IN0")

            cmd_len_bytes = 7

            prev_data = None
            last_x = None
            last_y = None
            last_z = None
            last_buttons = None

            while self.running:
                # read and process
                data = ser.read(cmd_len_bytes)

                # print hex_repr(data), repr(data)

                if data == prev_data:
                    continue

                prev_data = data

                # data = data[1:]

                assert ord(data[0]) & 0x80
                top_x = ord(data[0]) & 0x03

                high_x = ord(data[1]) & 0x7f   # bits 7-13 of x
                low_x = ord(data[2]) & 0x7f    # bits 1-6 of x
                x = top_x << 13 | high_x << 7 | low_x
                buttons = ord(data[3]) & 0x78  # buttons
                z_low = ord(data[3]) & 0x04    # lowest or 2nd lowest z bit (depending on max pressure)

                top_y = ord(data[3]) & 0x03
                high_y = ord(data[4]) & 0x7f   # bits 7-13 of x
                low_y = ord(data[5]) & 0x7f    # bits 1-6 of x
                y = top_y << 13 | high_y << 7 | low_y

                z_sign_bit = ord(data[6]) & 0x40
                z_sign = 1 if z_sign_bit else -1
                high_z = ord(data[6]) & 0x3f
                z = (high_z << 1 | z_low) * z_sign

                # print "x: %r y: %r buttons: %x z: %r" % (x, y, buttons, z)

                if (last_x, last_y) != (x, y):
                    x_scaled = float(x) / max_x
                    y_scaled = float(y) / max_y
                    self.control_interface.mouse_move(x_scaled, y_scaled)
                    last_x, last_y = x, y

                if (last_z, last_buttons) != (z, buttons):
                    self.control_interface.touch_change(buttons, z)
                    last_z, last_buttons = z, buttons

        finally:
            ser.close()
