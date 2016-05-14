import argparse

from control_interface import ControlInterface
from tabletcontrol import ProcessTabletSerialCommands


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("serial_port",
                        help="The serial port that your tablet is connected to (e.g. com1)")
    return parser.parse_args()


if __name__ == "__main__":
    ci = ControlInterface()
    options = parse_args()
    proc = ProcessTabletSerialCommands(options.serial_port, ci)
    proc.run()