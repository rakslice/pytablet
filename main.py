from control_interface import ControlInterface
from tabletcontrol import ProcessTabletSerialCommands

if __name__ == "__main__":
    ci = ControlInterface()
    proc = ProcessTabletSerialCommands("com3", ci)
    proc.run()