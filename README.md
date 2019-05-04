# ArdumowerDK
RF24_Mesh Serial Communication to Ardumower and other nodes


#Dependencies:
  Tested with:
	Win XP, Win Vista, Win 7, Win 8, Win 10, Linux
	
	nRF24 modules connected to Arduino's
	
  Arduino UNO
    RF24 librarry
    RF24_Network librarry
    RF24_Mesh librarry V1.04
    by TMRh20
    
	Python 2.7 32bit / Python 3
		Pyserial
		Matplotlib
    Pygame


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

#Mobile Devices can be notified via NotifyMyDevice service
  Enter your API tokken in API.txt


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