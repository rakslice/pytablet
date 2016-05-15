A quick thrown-together shim for using a Digitizer II (UD-608-R) on Windows 7/8/10 without a tablet driver.

### License ###

MIT; see the file COPYING

### Install ###

First you'll need [Python 2.7](https://www.python.org/downloads/release/python-2711/)

Then, to install the required libraries, run

    >c:\Python27\Scripts\pip.exe install -r requirements.txt

on the included requirements.txt file

### Usage ###

Run main.py with the serial port your tablet is on.

    >C:\Python27\python.exe main.py com3
	Opening serial port 'com3' at 9600 bps
	Serial port 'com3' opened
	Model string: 'UD-0608-R00 V1.4-4'
	Config string: 'E203C900,000,00,1270,1270'
	Max coordinates: '10240,07680'
	Enabling pressure mode
	Disabling incremental mode
	Starting main loop
	Ctrl-C to exit

As long as it is running, it will watch for pen actions on the tablet and send mouse action commands to Windows. 

### To-do: ###
- Pressure support, if possible (is there even a standard API for that?) 

