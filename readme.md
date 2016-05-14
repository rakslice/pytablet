A quick thrown-together shim for using a Digitizer II (UD-608-R) on Windows 7/8/10 without a tablet driver.

### License ###

MIT; see the file COPYING

### Install ###

First you'll need [Python 2.7](https://www.python.org/downloads/release/python-2711/)

Then, to install the required libraries, run

    c:\Python27\Scripts\pip.exe install -r requirements.txt

on the included requirements.txt file

### Usage ###

Run main.py with the serial port your tablet is on.

    C:\Python27\python.exe main.py com3

### To-do: ###
- Pressure support, if possible (is there even a standard API for that?) 

