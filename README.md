# ArdumowerDK
Bluetooth/WIFI Serial Communication to Ardumower


#Dependencies:
	Win XP, Win Vista, Win 7, Win 8, Win 10, Linux
	
	Bluetooth Serial emulation *COM port installed (outgoing) 
		
	WIFI serial connection
		by using HW "VSP3 - Virtual Serial Port" 
		from http://www.hw-group.com/products/hw_vsp/index_en.html#download
		Single-port version of HW VSP3 is available freely...
		
	nRF24 Modules connected to Arduino Uno's can be interfaced using 
	RF24 branch of this repo and the RF24 Arduino librarry from TMRH20
	
	ArdumowerDK will scan all available comports and send {.} (or you just choose one)
	while listening to an "Ardumower" reply to determine if talking to Ardumower or not
	
	Python 2.7 32bit / Python 3
		Pyserial
		Matplotlib


#Keyboard shortcuts:
	Up: manual forward
	down: manual stop
	left: manual left
	right: manual right
	b: maunal back
	F1: manual mower off
	
	a: automatic mode
	Esc: OFF
	Page up: not yet implemented
	page down: not yet implemented

#Debug Window  (View/Debug)
	 ',' or '|' or '{' or '}' should not be used in the debug strings 
	 since these characters are used for filtering normal communication (commands/plot data) 

#Save settings to file
	it's now possible to save your mowers settings to ta txt file
	Timer settings are ignored



#use at your own risk

	 
thanks go to:
Jacob Hallén
http://code.activestate.com/recipes/82965-threads-tkinter-and-asynchronous-io/
for the io_threading recipe
and
Dan Savilonis
https://github.com/djs/serialenum
for a multiplatform serial enumeration possibility
and
vegaseat
http://www.daniweb.com/forums/post202523-3.html 
for the ringbuffer
and
Michael Lange 
http://tkinter.unpythonic.net/wiki/ProgressMeter
for the statusbar / class meter

and 
Sebastian Held and Frederic Goddeeris and the all the active developpers of the Ardumower Project
http://ardumower.de

and as always: thanks for all the fish