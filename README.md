# ArdumowerDK
Bluetooth Serial Communication to Ardumower


#Dependencies:
	Win XP, Win Vista, Win 7, Win 8, Win 10, (Linux)
	
	Bluetooth Serial emulation *COM port installed (outgoing) 
		ArdumowerDK will scan all available comports and send {.},
		while listening to an "Ardumower" reply to determine if talking to Ardumower or not
		if no Ardumower is found some debug messages (kind of simulation mode) 
		will be sent to the program and the plot will automatically load and plot some data.
		No comport has to be set. 
		
	Python 2.7 32bit
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