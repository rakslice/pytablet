import sys

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
    """ Read from the tablet and do appropriate event calls on control_interface
    """
    def __init__(self, serial_port_device_name, control_interface):
        assert isinstance(control_interface, ControlInterface)
        self.control_interface = control_interface
        self.serial_port_device_name = serial_port_device_name
        self.running = False

    def log(self, msg):
        print >> sys.stderr, msg

    def stop(self):
        self.running = False

    def run(self):
        self.running = True

        # https://pythonhosted.org/pyserial/shortintro.html#opening-serial-ports
        baudrate = 9600

        self.log("Opening serial port %r at %r bps" % (self.serial_port_device_name, baudrate))
        ser = serial.Serial()
        ser.baudrate = baudrate
        ser.port = self.serial_port_device_name
        ser.open()
        try:

            # protocol description:
            # http://linuxwacom.sourceforge.net/wiki/index.php/Serial_Protocol_IV

            # check which port was really used
            self.log("Serial port %r opened" % ser.name)

            # query model
            ser.write("~#")
            ser.read(2)

            model = read_to_cr(ser)
            self.log("Model string: %r" % model)

            # iv
            # ser_cmd(ser, "\r#")

            config_string = ser_cmd_w_response(ser, "~R")
            self.log("Config string: %r" % config_string)

            max_coordinates = ser_cmd_w_response(ser, "~C")
            self.log("Max coordinates: %r" % max_coordinates)
            max_x, max_y = [int(v) for v in max_coordinates.split(",")]

            # max rate

            # in principle this command is supposed to tell the tablet to switch to a faster baud rate
            ser_cmd(ser, "IT0")

            # I was expecting to then have to bump up the baud rate on the serial port before issuing further commands.
            # But actually I continued to be able to communicate without doing that, and doing that made further
            # communications fail.
            # I don't know if this is because of:
            #  - A misunderstanding about the command
            #  - Digitizer II not supporting a faster rate?
            #  - A problem with pyserial
            #  - A quirk of my USB-serial adapter
            #  - Something else

            # Bump up to the new baud rate

            # time.sleep(0.125)

            # print "closing"
            # ser.close()
            # ser = serial.Serial()
            # ser.baudrate = 19200
            # ser.port = self.serial_port_device_name
            # print "reopening"
            # ser.open()

            # time.sleep(0.125)
            #
            # Okay, we should be able to talk to the tablet again now
            #
            # ser.write("~#")
            # ser.read(2)
            #
            # model_again = read_to_cr(ser)
            # assert(model_again == model)
            #

            # Other settings

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

            # We use timeout mode so we can get KeyboardInterrupt in a sec without any tablet events happening
            ser.timeout = 1

            self.log("Starting main loop")
            self.log("Ctrl-C to exit")

            try:

                while self.running:
                    # read and process

                    data = ser.read(cmd_len_bytes)
                    # could be a null or partial read due to timeout
                    while len(data) < cmd_len_bytes:
                        data += ser.read(cmd_len_bytes - len(data))

                    # print hex_repr(data), repr(data)

                    if data == prev_data:
                        continue

                    prev_data = data

                    # TODO: resync rather than just failing if we get out of sync

                    assert ord(data[0]) & 0x80, "Leading byte of frame didn't have MSB set. Are we out of sync?"
                    top_x = ord(data[0]) & 0x03    # bits 14-15 of x

                    high_x = ord(data[1]) & 0x7f   # bits 7-13 of x
                    low_x = ord(data[2]) & 0x7f    # bits 1-6 of x
                    x = top_x << 13 | high_x << 7 | low_x
                    buttons = ord(data[3]) & 0x78  # buttons
                    z_low = ord(data[3]) & 0x04    # lowest or 2nd lowest z bit (depending on max pressure)

                    top_y = ord(data[3]) & 0x03    # bits 14-15 of y
                    high_y = ord(data[4]) & 0x7f   # bits 7-13 of y
                    low_y = ord(data[5]) & 0x7f    # bits 1-6 of y
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

            except KeyboardInterrupt:
                self.log("Exiting")

        finally:
            ser.close()
