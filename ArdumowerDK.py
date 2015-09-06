#-------------------------------------------------------------------------------
# Name:        Ardumower DK
# Purpose:     Communication Ardumower - Windows computer via Bluetooth serial port
#
# Author:      Holoratte
#
# Created:     06.09.2015
# Copyright:   (c) Holoratte 2015
# Licence:     Just use it. Selling this software might be prohibited.
# Version:     15
#-------------------------------------------------------------------------------

"""
This recipe describes how to handle asynchronous I/O in an environment where
you are running Tkinter as the graphical user interface. Tkinter is safe
to use as long as all the graphics commands are handled in a single thread.
Since it is more efficient to make I/O channels to block and wait for something
to happen rather than poll at regular intervals, we want I/O to be handled
in separate threads. These can communicate in a threasafe way with the main,
GUI-oriented process through one or several queues. In this solution the GUI
still has to make a poll at a reasonable interval, to check if there is
something in the queue that needs processing. Other solutions are possible,
but they add a lot of complexity to the application.

Created by Jacob Hallén, AB Strakt, Sweden. 2001-10-17
"""


import Tkinter as tk
import time
import threading
import random
import Queue
##import statusbar
import Ringbuffer
import serial
import tkMessageBox
import tkFileDialog
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import platform
import serialenum
import csv
import datetime

class GuiPart:
    def __init__(self, master, receivedQueue, sendQueue, receiveConnected_Queue,
                    saveToFile_Queue, logToFile_Queue, endCommand, Debug, Com):

        self.master = master
        self.lastCommand = []
        for i in range(100):
            self.lastCommand.append(".")
        self.settingsfname = ""
        self.logFileName= ""
        self.settingsToFile = False
        self.settingsFromFile = False
        self.logToFile = False
        self.mainSettingsComand_list = []
        self.mainSettingsName_list = []
        self.snl_index = 0
        self.numberOfSetting = 0
        self.RQueue = receivedQueue
        self.SQueue = sendQueue
        self.sTfQueue = saveToFile_Queue
        self.rCQueue = receiveConnected_Queue
        self.lTfQueue = logToFile_Queue
            # Set up the GUI

        #---------------Menu--------------------------------------------
        def donothing():
           filewin = tk.Toplevel(master)
           button = tk.Button(filewin, text="not yet implemented ;-(")
           button.pack()
        def showversion():
           filewin = tk.Toplevel(master)
           button = tk.Button(filewin, text="ArdumowerDK V15")
           button.pack()

        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff = 0)
##        filemenu.add_command(label="New", command=donothing)
##        filemenu.add_command(label="Open", command=donothing)
##        filemenu.add_command(label="Save", command=donothing)
##        filemenu.add_command(label="Save as...", command=donothing)
##        filemenu.add_command(label="Close", command=donothing)
##
##        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=endCommand)
        menubar.add_cascade(label="File", menu=filemenu)
##        editmenu = tk.Menu(menubar, tearoff=0)
##        editmenu.add_command(label="Undo", command=donothing)
##
##        editmenu.add_separator()

##        editmenu.add_command(label="Cut", command=donothing)
##        editmenu.add_command(label="Copy", command=donothing)
##        editmenu.add_command(label="Paste", command=donothing)
##        editmenu.add_command(label="Delete", command=donothing)
##        editmenu.add_command(label="Select All", command=donothing)
##
##        menubar.add_cascade(label="Edit", menu=editmenu)


        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Debug", command=Debug)
        viewmenu.add_command(label="Connect", command=Com)
##        viewmenu.add_command(label="", command=donothing)
##        viewmenu.add_command(label="", command=donothing)
        menubar.add_cascade(label="View", menu=viewmenu)

        settingsmenu = tk.Menu(menubar, tearoff=0)
        settingsmenu.add_command(label="save", command=lambda: self.send("sz"))
        settingsmenu.add_command(label="save to file", command= self.save_settings_toFile)
        settingsmenu.add_command(label="load from file", command=donothing)
##        settingsmenu.add_command(label="load from file", command=self.load_settings_fromFile)
        settingsmenu.add_command(label="load fatory settings", command=lambda: self.send("sx"))
        settingsmenu.add_command(label="Edit", command=lambda: self.send("s"))
        menubar.add_cascade(label="Settings", menu=settingsmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=showversion)
        menubar.add_cascade(label="Help", menu=helpmenu)

        master.config(menu=menubar)


        #--------------------Buttons and scalebars----------------------------------------------


        self.console1 = tk.Button(master, text='Main', command= self.mainmenu)
        self.console1.grid(column = 0, row =0)
        self.console1.grid_remove()
##        console2 = tk.Button(master, text='Refresh', command=lambda: self.send(self.lastCommand[-1],"refresh"))
##        console2.grid(column = 2, row =1)
##        console3 = tk.Button(master, text='Back', command=lambda: self.send(self.lastCommand[-2],"back"))
##        console3.grid(column = 3, row =1)
##        self.m1 = statusbar.Meter(root, relief='ridge', bd=3, width = 300)
##        self.m1.grid(row=4, column=1)
        self.nav_buttons = []
        self.scale = []
        self.scaleVar = []
        self.main_buttons = []
        self.maincommand_list = []
        self.maincomName_list = []
        self.titles = []
        coma = "xxx"
        for i in range(10):
            self.main_buttons.append(tk.Button(master, text='-', command = lambda: self.send("")))
            if i >= 5:
                self.main_buttons[i].grid(row =1, column = i-3)
            else:
                self.main_buttons[i].grid(row =0, column = i+1)
            self.main_buttons[i].grid_remove()
        for i in range(35):
            self.nav_buttons.append(tk.Button(master, text='-', command = lambda: self.send("")))
            if i >= 12:
                self.nav_buttons[i].grid(row =i - 6, column = 3)
            else:
                self.nav_buttons[i].grid(row =i + 6, column = 1)
            self.nav_buttons[i].grid_remove()
        for i in range(35):

            self.scaleVar.append(tk.DoubleVar())
            self.scale.append(tk.Scale(master, variable = self.scaleVar[i],  orient='horizontal', resolution=1, from_=0, to= +100))
            if i >= 12:
                self.scale[i].grid(column = 4, row=i-6, sticky = "ew")
            else:
                self.scale[i].grid(column = 2, row=i+6, sticky = "ew")
            self.scale[i].grid_remove()

#        -----------------------------------Plot---------------------------
        self.canvasnumber =9 #number of subsubplots (1-9)
        self.plot = False
        self.channel = 0
        self.f = Figure()
        self.ax = []
        self.lines =[]
        self.plotylabels=[]
        self.plotxlabels = []
        self.plotnames = []
        self.tdata = [0]
        self.data = [0]
        self.lo = []
        self.hi = []

        for i in range(50):
            self.lo.append(0.0)
            self.hi.append(0.0)
            self.plotnames.append("value")

        self.canvas = []
        self.backgrounds = []
        self.c=FigureCanvasTkAgg(self.f, master=master)
        self.c.get_tk_widget().grid(column=10, row=0, rowspan =20, columnspan = 1)
        self.c.get_tk_widget().grid_remove()
        self.toolbar = NavigationToolbar2TkAgg( self.c, master )
        self.toolbar.grid(column=10, row=30, sticky="w")
        self.toolbar.update()
        self.canvas = []

        for i in range(self.canvasnumber):
            self.backgrounds.append(None)
            self.plotxlabels.append("Time")
            self.plotylabels.append(self.plotnames[i])
            self.ax.append(self.f.add_subplot(11+i+(self.canvasnumber*100)))
            self.lines.append(Line2D(self.tdata, self.data, animated=True))
            self.ax[i].add_line(self.lines[i])
            self.ax[i].set_ylim(-10.1, 255.0)
            self.ax[i].set_xlim(1, 300)
            self.ax[i].set_xlabel(self.plotxlabels[i])
            self.ax[i].set_ylabel(self.plotylabels[i])
            self.ax[i].yaxis.set_major_formatter(FormatStrFormatter('%d'))
            self.canvas.append(self.ax[i].figure.canvas)

        self.c.mpl_connect('draw_event',self.update_background)
        self.f.subplots_adjust(hspace=0.1)

        for a in self.f.axes[:-1]:
            a.set_xlabel("")
            a.set_xticks([])

        self.channel = 0

        self.plotnumbers = [0]
        self.datasize = 300
        self.data_list =[]
        self.datanumber = 0
        self.timeSent = False
        self.idle_flag = True
        self.idle1_flag = True


        # Add more GUI stuff here

        master.bind('<Escape>', self.sendoff)
        master.bind('<Left>', self.sendLeft)
        master.bind('<Right>', self.sendRight)
        master.bind('<Up>', self.sendUp)
        master.bind('<Down>', self.sendDown)
        master.bind('<b>', self.sendB)
        master.bind('<F1>', self.sendF1)
        master.bind('<Prior>', self.sendPrior)
        master.bind('<Next>', self.sendNext)
        master.bind('<a>', self.sendAutomode)


    def create_csv(self):
##        print'doing'
        date= str(datetime.datetime.now().replace(microsecond=0))
        date, time= date.split()
##        time , gmt= time.split('+')

        hh,mm,ss=time.split(':')
        self.logFileName += "_" + date+' '+hh+'-'+mm+'-'+ss+'.csv'
        with open(self.logFileName, "wb" ) as f:
            writer = csv.writer(f)
            writer.writerow( ("ARDUMOWER SENSOR LOG FILE") )
        return True
##        print 'done'


    def write_csv(self,datetime,data):
        datetime=str(datetime.replace(microsecond=0))
        date, time= datetime.split()
        if data[0].find("time") >= 0:
            data.insert(0,"Time")
            data.insert(0,"Date")
        else:
            data.insert(0,time)
            data.insert(0,date)
##        time , gmt= time.split('+')
        try:
            with open(self.logFileName, 'ab' ) as f:
                writer = csv.writer(f, dialect='excel')
                writer.writerow(data)
        except:
            print "cannot write so fast"
            pass

    def save_settings_toFile(self,fname = ""):
        if fname == "": fname = tkFileDialog.asksaveasfilename( title='Save to file', filetypes=[("Ardumower settings","*.ardm" ),],defaultextension="*.ardm")
        if fname != "":
            self.settingsfname = fname
            msg = "settings_toFile"
            self.settingsToFile = True
            self.rCQueue.put(msg)
            self.send("s")

    def load_settings_fromFile(self,fname = ""):
        if fname == "": fname = tkFileDialog.askopenfilename( title='Load from file', filetypes=[("Ardumower settings","*.ardm" ),("all files", "*.*")],defaultextension="*.ardm")
        if fname != "":
            self.settingsfname = fname
            msg = "settings_fromFile"
            self.settingsFromFile = True
            self.rCQueue.put(msg)
            self.send("s")


    def update_background(self,event):
        for i in range(len(self.backgrounds)):
            self.backgrounds[i] = self.canvas[i].copy_from_bbox(self.ax[i].bbox)

    def update_plots(self, tdata1=[], data=[], channel=0,dnumber=0, *args):

        if len(tdata1) == len(data):
            if self.backgrounds[channel] is None: return True
            self.canvas[channel].restore_region(self.backgrounds[channel])
            self.lines[channel].set_data(tdata1, data)
    ##        self.ax[channel].set_xlim(min(tdata1), max(tdata1))
            if len(data)>=0:
                lo,hi=float(min(data)), float(max(data))
                if lo <= self.lo[dnumber] or hi>= self.hi[dnumber]:
                    self.lo[dnumber], self.hi[dnumber]=float(lo)-1,float(hi)+1
                    self.ax[channel].set_ylim(self.lo[dnumber], self.hi[dnumber])

                    self.master.after_idle(self.ax[channel].figure.canvas.draw)
                    for i in range(self.canvasnumber):
                        self.master.after_idle(self.ax[i].draw_artist,self.lines[i])
                    for i in range(self.canvasnumber):
                        self.master.after_idle(self.canvas[i].blit,self.ax[i].bbox)


    ##        self.ax[channel].cla()
                else:
                    self.ax[channel].draw_artist(self.lines[channel])
                    self.canvas[channel].blit(self.ax[channel].bbox)

        self.toolbar.update()
        self.idle1_flag = True
        return True

    def sendLeft(self,event):
        self.mainmenu()
        self.send("nl")
    def sendRight(self,event):
        self.mainmenu()
        self.send("nr")
    def sendUp(self,event):
        self.mainmenu()
        self.send("nf")
    def sendDown(self,event):
        self.mainmenu()
        self.send("ns")
    def sendB(self,event):
        self.mainmenu()
        self.send("nb")
    def sendF1(self,event):
        self.mainmenu()
        self.send("nm")
    def sendPrior(self,event):
        pass
##        self.send("")
    def sendNext(self,event):
        pass
##        self.send("")
    def sendoff(self,event):
        self.send("ro")

    def sendAutomode(self,event):
        self.send("ra")

    def send(self, command, value = None):
        if command == "sx":
            if tkMessageBox.askokcancel("Factory Reset", "Do You really want to reset all setting to factory default?"):
                self.SQueue.put(command)
        elif command == "sz":
            if tkMessageBox.askokcancel("Save Setting", "Do You really want to save the settings to the eeprom?"):
                self.SQueue.put(command)
        elif command =="m1":
            fname = ""
            fname = tkFileDialog.asksaveasfilename( title='Save Sensor log to file', filetypes=[("comma separated value","*.csv" )])
            if fname != "":
                self.logFileName = fname
                if self.create_csv():
                    self.rCQueue.put("log")
                    self.logToFile = True
                    self.SQueue.put(command)
                else:
                    self.rCQueue.put("no log")
                    self.logToFile = False
            else:
                self.rCQueue.put("no log")
                self.logToFile = False

        else:
            self.rCQueue.put("no log")
            self.logToFile = False
            if value == None and command!= "sz" and command!= "sx": self.lastCommand.append(command)
            if value != None:
                if value == "back":
                    if len(self.lastCommand) >= 1: del self.lastCommand[-1]
                elif value== "refresh":
                    pass
                else:
                    command += "`" + str(value)
            self.SQueue.put(command)


    def mainmenu(self):
        self.plot = False
        self.RQueue.put("{.Ardumower (Ardumower)|r~Commands|n~Manual|s~Settings|in~Info|c~Test compass|m1~Log sensors|yp~Plot|y4~Error counters|y9~ADC calibration}init")
        self.send("s")
        self.console1.grid_remove()
        for d in range(len(self.nav_buttons)):
            self.nav_buttons[d].configure(relief = tk.RAISED)

    def setplot(self,buttonpressed):
##        if (len(self.plotnumbers)-1)<=self.canvasnumber:
            for i in range(len(self.nav_buttons)):
                if self.nav_buttons[i].cget("relief") == "ridge":
                    if i not in self.plotnumbers: self.plotnumbers.append(i)
            if buttonpressed not in self.plotnumbers:
                self.plotnumbers.append(buttonpressed)
                self.nav_buttons[buttonpressed].configure(relief = tk.RIDGE)
            else:
                self.plotnumbers.remove(buttonpressed)
                self.nav_buttons[buttonpressed].configure(relief = tk.RAISED)

            for lo in self.lo:
                lo = 0.0
            for hi in self.hi:
                hi = -1.0
            self.plotnumbers.sort()

            self.idle_flag = False
            for i in range(self.canvasnumber):
                if len(self.plotnumbers)>= (i+1):
                    try:
                        self.ax[i].set_ylabel(self.plotnames[self.plotnumbers[i]])
                        self.ax[i].set_ylim(self.lo[self.plotnumbers[i]], self.hi[self.plotnumbers[i]])
                        self.master.after_idle(self.ax[i].figure.canvas.draw)
                    except: pass
                else:
                    self.ax[i].set_ylabel("")
                    self.ax[i].set_ylim(0,0)
                    self.master.after_idle(self.ax[i].figure.canvas.draw)
            self.idle_flag = True


    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.RQueue.qsize():
            msg_list = []
            data_list = []
            self.command_list = []
            self.comName_list = []

            self.multiplier_list = []
            self.scaleActiv_list = []
            self.minimum_list = []
            self.maximum_list = []
            self.ist_list = []
            multiplier = 0
            init = False
            try:
                msg = self.RQueue.get(0)
                # Check contents of message and do what it says
##                print "r msg: ",msg
                if msg.find("init") >= 0:
                    msg.strip("init")
                    init = True
                    msg = msg.strip("init")

                msg = msg.strip("\n")
                msg = msg.strip("\r")

                if msg.find("|") >= 0:
                    msg = msg.strip("{")
                    msg = msg.strip("}")
                    msg = msg.strip(".")
                    msg = msg.strip("=")

                    msg_list = msg.rsplit("|")
                elif msg.find("Log sensors") >= 0:
                    msg = msg.strip("{")
                    msg = msg.strip("}")
                    msg = msg.strip(".")
                    msg = msg.strip("=")
                    msg_list.append(msg)


                elif msg.find(",") >= 0 and not self.logToFile:
                    data_list = msg.rsplit(",")
                    for i in range(len(data_list)):
                        data_list[i] = float(data_list[i])
                else:
                    print"msg error:" , msg
                    pass
                if not self.plot:
                    for i in range(len(self.nav_buttons)):
                        self.nav_buttons[i].grid_remove()
                        self.scale[i].grid_remove()

                if len(msg_list) >= 1 or self.plot:
    ##
                    if init:
                        self.titles = []
                        self.maincommand_list=[]
                        self.maincomName_list = []
                        self.c.get_tk_widget().grid_remove()
##                        self.toolbar.grid_remove()
                        for i in range(len(msg_list)-1):
                            coma, comName = msg_list[i+1].split("~")
                            self.maincommand_list.append(coma)
                            self.maincomName_list.append(comName)
                            self.main_buttons[i].grid()
                            self.main_buttons[i].configure(text=self.maincomName_list[i], command= lambda i=i: self.send(self.maincommand_list[i]))
                            self.titles.append(comName)
                        init = False
##                            self.console1.grid()

                    elif self.plot:
                        if len(msg_list)>=2:
                            if msg_list[0].find("`")>=0:
                                title,self.datasize = msg_list[0].split("`")
                            if msg_list[1].find("`")>=0:
                                for i in range(len(msg_list)-1):
                                    msg_list[i+1], num = msg_list[i+1].split("`")
                            for name in self.plotnames:
                                name = "value"
                            self.idle_flag = False
                            for i in range(self.canvasnumber):
                                self.ax[i].set_xlim(1, int(self.datasize))
                                self.ax[i].set_ylabel("value")
                                self.ax[i].set_ylim(0,0)
                                self.master.after_idle(self.ax[i].figure.canvas.draw)

                            self.data_list = []
                            self.lo = []
                            self.hi = []
                            self.plotnumbers = [0]
                            for i in range(len(self.main_buttons)):
                                    self.main_buttons[i].configure(relief = tk.RAISED)

                            for tiltle in self.titles:
                                ti = tiltle
                                if msg_list[0].find(ti) >= 0:
                                    tiltlenumber = self.titles.index(tiltle)
                                    self.main_buttons[tiltlenumber].configure(relief = tk.RIDGE)
                            if msg_list[1].find("time")>=0:
                                msg_list = msg_list[1:]
                                self.timeSent = True
                            else: self.timeSent = False
                            for i in range(len(msg_list)-1):
                                self.data_list.append(Ringbuffer.RingBuffer(int(self.datasize)))

                                self.hi.append(0.0)
                                self.lo.append(0.0)

                            for i in range(len(self.nav_buttons)):self.nav_buttons[i].grid_remove()
                            for i in range(len(msg_list)-1):
                                self.nav_buttons[i].grid()
                                if i <= (self.canvasnumber-1) :
                                    if i not in self.plotnumbers:self.plotnumbers.append(i)
                                    self.nav_buttons[i].configure(text=msg_list[i+1],relief = tk.RIDGE, command=lambda i= i:self.setplot(i))
                                    self.ax[i].set_ylabel(msg_list[i+1])
                                else:
                                    if i in self.plotnumbers: self.plotnumbers.remove(i)
                                    self.nav_buttons[i].configure(text=msg_list[i+1], relief = tk.RAISED,command=lambda i= i:self.setplot(i))
                                self.plotnames[i] = msg_list[i+1]

                            self.idle_flag = True


                        elif len(data_list)>=1:
                            t0 = time.time()
                            if self.timeSent:
                                data_list = data_list[1:]
                            for i in range(len(data_list)):
                                self.data_list[i].append(data_list[i])
                            self.datanumber +=1
                            try:
                                if self.idle_flag and self.idle1_flag:
                                    self.idle1_flag = False
                                    tdata1 = []
                                    if len(self.plotnumbers) >=1:
                                        for i in range(len(self.data_list[self.plotnumbers[0]])):
                                            tdata1.append(i)
                                    for i in range(self.canvasnumber):
                                        if len(self.plotnumbers)>= (i+1):
                                            self.channel = i

    ##                                        if (len(self.data_list)-1) >= len(self.data_list[self.plotnumbers[i]]):
                                            self.idle1_flag = False
                                            self.master.after_idle(self.update_plots,tdata1,self.data_list[self.plotnumbers[i]], self.channel,self.plotnumbers[i])
        ##                                        if self.update_plots(tdata1,self.data_list[self.plotnumber+i], self.channel,i):pass

                                    self.datanumber = 0
                            except:
                                pass



                    else:
                        for tiltle in self.titles:
                            if tiltle =="Test compass":
                                ti = "Compass"
                            else: ti = tiltle
                            if msg_list[0].find(ti) >= 0:
                                tiltlenumber = self.titles.index(tiltle)

                                if tiltlenumber == 6:
                                    self.rCQueue.put("no log")
                                    self.logToFile = False
                                    for button in self.main_buttons:
                                        button.grid_remove()
                                    self.titles=[]

                                    self.c.get_tk_widget().grid()
                                    self.toolbar.grid()
                                    self.plot = True
                                    self.maincommand_list = []
                                    self.maincomName_list = []
                                    for d in range(len(self.main_buttons)):
                                            self.main_buttons[d].configure(relief = tk.RAISED)
                                    for i in range(len(msg_list)-1):
                                        coma, comName = msg_list[i+1].split("~")
                                        self.maincommand_list.append(coma)
                                        self.maincomName_list.append(comName)
                                        self.main_buttons[i].configure(text=self.maincomName_list[i], command= lambda i=i: self.send(self.maincommand_list[i]))
                                        self.main_buttons[i].grid()
                                        self.titles.append(comName)
                                        self.console1.grid()
                                elif tiltlenumber == 5:
                                    self.plot = False
                                    for i in range(len(self.main_buttons)):
                                        self.main_buttons[i].configure(relief = tk.RAISED)
                                    self.main_buttons[tiltlenumber].configure(relief = tk.RIDGE)


                                else:
                                    self.rCQueue.put("no log")
                                    self.logToFile = False
                                    self.plot = False
                                    for i in range(len(self.main_buttons)):
                                        self.main_buttons[i].configure(relief = tk.RAISED)
                                    self.main_buttons[tiltlenumber].configure(relief = tk.RIDGE)

                        if not self.plot:
                            for i in range(len(msg_list)-1):
                                self.scaleActiv_list.append(False)
                                if msg_list[i+1].find("~ ~") >= 0:
                                    coma, comName, a, multiplier = msg_list[i+1].split("~")
                                    comName, ist , maximum, minimum = comName.split("`")
                                    self.scaleActiv_list[i] = True

                                else:coma, comName = msg_list[i+1].split("~")

                                self.command_list.append(coma)
                                self.comName_list.append(comName)
                                self.multiplier_list.append(0.0)
                                self.minimum_list.append(0)
                                self.maximum_list.append(0)
                                self.ist_list.append(0)
                                self.nav_buttons[i].grid()
                                self.nav_buttons[i].configure(text=comName, command= lambda i=i: self.send(self.command_list[i]))
                                if self.scaleActiv_list[i] == True:
                                    self.multiplier_list[i] = float(multiplier)
                                    self.minimum_list[i] = float(minimum)* self.multiplier_list[i]
                                    self.maximum_list[i] = float(maximum) * self.multiplier_list[i]
                                    self.ist_list[i] = float(ist) * self.multiplier_list[i]
                                    self.scale[i].configure(variable = self.scaleVar[i], resolution=self.multiplier_list[i], from_=self.minimum_list[i], to_= self.maximum_list[i])
                                    self.scale[i].grid()
                                    self.scaleVar[i].set(self.ist_list[i])
                                    self.nav_buttons[i].configure(text=comName, command= lambda i=i: self.send(self.command_list[i], self.scaleVar[i].get()/self.multiplier_list[i]))

            except Queue.Empty:
                pass

        if self.logToFile:
            while self.lTfQueue.qsize():
                try:
                    msg = self.lTfQueue.get(0)
                    msg = msg.strip("\n")
                    msg = msg.strip("\r")
                    datalist = msg.rsplit(",")
                    self.write_csv(datetime.datetime.now(),datalist)
##                    print msg
                    msg = ""
                except Queue.Empty:
                    pass

        if self.settingsToFile:
            while self.sTfQueue.qsize():

                try:
                    msg = self.sTfQueue.get(0)
                    msg = msg.strip("\n")
                    msg = msg.strip("\r")
                    settings_list = []

                    if msg.find("|") >= 0:
                        msg = msg.strip("{")
                        msg = msg.strip("}")
                        msg = msg.strip(".")
                        msg = msg.strip("=")

                        msg_list = msg.rsplit("|")

                    # Check contents of message and do what it says
                        for i in range(len(msg_list)-1):
                            if msg_list[i+1].find("~ ~") >= 0:
                                coma, comName, a, multiplier = msg_list[i+1].split("~")
                                comName, ist , maximum, minimum = comName.split("`")
                                tabubaltor = "\t"
                                descriptor = comName +" (maximum:"+ maximum + " minimum:"+ minimum + ") " + " X " + multiplier
                                numberOfTabs = int((75 - len(descriptor))/4)+1
                                for j in range(numberOfTabs): tabubaltor += "\t"
                                setting = descriptor + tabubaltor + "|" + coma + "`" + ist
                            else:
                                coma, comName = msg_list[i+1].split("~")
                                tabubaltor = "\t"
                                descriptor = comName
                                numberOfTabs = int((75 - len(descriptor))/4)+1
                                for j in range(numberOfTabs): tabubaltor += "\t"
                                setting = descriptor + tabubaltor + "|" + coma

                            if msg_list[0].find("Settings") >= 0:
                                if (coma.find("sz") == -1) and (coma.find("sx") == -1):
                                    comName = comName.upper()
                                    self.mainSettingsName_list.append(comName)
                                    self.mainSettingsComand_list.append(coma)
                            else:
                                if setting.find("\n") == -1:
                                    settings_list.append(setting)

                        if msg_list[0].find("Settings") >= 0:
                            self.snl_index  = 0
                            with open(self.settingsfname,"w") as settingsFile:
                                settingsFile.write("SETTINGS ARDUMOWER"+ time.strftime("%Y-%m-%d %H:%M:%S") + "\n\n\n\n")
                        else:
                            tabubaltor = "\t"
                            descriptor = self.mainSettingsName_list[self.snl_index]
                            numberOfTabs = int((75 - len(descriptor))/4)+1
                            for j in range(numberOfTabs): tabubaltor += "\t"
                            mainSet = descriptor + tabubaltor + "|" + self.mainSettingsComand_list[self.snl_index]  + "\n"

                            with open(self.settingsfname,"a") as settingsFile:
                                settingsFile.write(mainSet)
                                for setting in settings_list:
                                    settingsFile.write(setting + "\n")
                                settingsFile.write("\n\n\n")
                            self.snl_index += 1

                        if self.snl_index +1  <= (len(self.mainSettingsComand_list)): self.send(self.mainSettingsComand_list[self.snl_index])
                        else:
                            self.rCQueue.put("not_settingsToFile")
                            self.settingsToFile = False
                            self.snl_index = 0


                except Queue.Empty:
                    pass

class GuiDebug(tk.Toplevel):
    def __init__(self, master, receive_connected_queue, sendQueue):
        tk.Toplevel.__init__(self)
        self.master = master
        self.title("Debug")
        self.geometry('+70+10')
        self.debug_entry_var=tk.StringVar()
        self.debug_entry = tk.Entry(self, textvariable = self.debug_entry_var)
        self.debug_entry.grid(column = 3, row =4)
        self.debug_entry_in_var=tk.StringVar()
        self.debug_entry_in = tk.Entry(self, textvariable = self.debug_entry_in_var)
        self.debug_entry_in.grid(column = 3, row =5, sticky="nesw")
        self.debug_text = tk.Text(self,width=100, height = 20)
        self.debug_entry_var.set("")
        self.debug_text_scrollbar = tk.Scrollbar(self)
        self.debug_text.config(yscrollcommand=self.debug_text_scrollbar.set)
        self.debug_text_scrollbar.config(command=self.debug_text.yview)
        self.debug_text.grid(row=6,column=3,sticky="nesw")
        self.debug_text_scrollbar.grid(row=6,column=3,sticky="nesw")
        def send_debug_command():
            sendQueue.put(self.debug_entry_var.get())
        self.sendbutton = tk.Button(self, text='Send', command= send_debug_command)
        self.sendbutton.grid(column = 3, row =4, sticky = "e")
        self.autoscroll_checkbutton_var = tk.IntVar()
        self.autoscroll_checkbutton_var.set(1)
        self.autoscroll_checkbutton = tk.Checkbutton(self, text = "Autoscroll", variable = self.autoscroll_checkbutton_var)
        self.autoscroll_checkbutton.grid(column = 3, row = 7, sticky= "e")
        self.sheepReply_checkbutton_var = tk.IntVar()
        self.sheepReply_checkbutton_var.set(0)
        self.sheepReply_checkbutton = tk.Checkbutton(self, text = "listen to sheep", variable = self.sheepReply_checkbutton_var)
        self.sheepReply_checkbutton.grid(column = 3, row = 8, sticky = "w")
        self.sheepSend_checkbutton_var = tk.IntVar()
        self.sheepSend_checkbutton_var.set(0)
        self.sheepSend_checkbutton = tk.Checkbutton(self, text = "sent to sheep", variable = self.sheepSend_checkbutton_var)
        self.sheepSend_checkbutton.grid(column = 3, row = 7, sticky = "w")
        self.plotingdata_checkbutton_var = tk.IntVar()
        self.plotingdata_checkbutton_var.set(0)
        self.plotingdata_checkbutton = tk.Checkbutton(self, text = "plot data", variable = self.plotingdata_checkbutton_var)
        self.plotingdata_checkbutton.grid(column = 3, row = 7)
        def getDebug(a,b,c):
            if self.plotingdata_checkbutton_var.get() == 1: receive_connected_queue.put("Data Debug")
            if self.plotingdata_checkbutton_var.get() == 0: receive_connected_queue.put("Data noDebug")
            if self.sheepReply_checkbutton_var.get() == 1: receive_connected_queue.put("Sheep Debug")
            if self.sheepReply_checkbutton_var.get() == 0: receive_connected_queue.put("Sheep noDebug")
            if self.sheepSend_checkbutton_var.get() == 1: sendQueue.put("Sent Debug")
            if self.sheepSend_checkbutton_var.get() == 0: sendQueue.put("Sent noDebug")
        self.sheepReply_checkbutton_var.trace("w",getDebug)
        self.plotingdata_checkbutton_var.trace("w",getDebug)
        self.sheepSend_checkbutton_var.trace("w",getDebug)
        self.withdraw()

class GuiConnect(tk.Toplevel):
    def __init__(self, master,initQueue, close_com):
        tk.Toplevel.__init__(self)
        self.initQueue = initQueue
        self.master = master
        self.title("Connection")
        self.geometry('+300+10')
        self.connection_entry_var=tk.StringVar()
        self.connection_entry = tk.Entry(self, textvariable = self.connection_entry_var, width = 50)
        self.connection_entry.grid(column = 3, row =0)
        self.options_var=tk.StringVar()
        self.connection_options = []
        def scan():
            self.connection_options = []
            self.connection_options = serialenum.enumerate()
##        self.connection_options.append("Network")
            self.connection_options.append("")
            self.options_var.set(self.connection_options[-1])
            self.options = apply(tk.OptionMenu,(self,self.options_var)+tuple(self.connection_options))
            self.options.grid(column = 3, row = 5, sticky = "w")

        scan()
##        self.___entry_in_var=tk.StringVar()
##        self.___entry_in = tk.Entry(self, textvariable = self.___entry_in_var)
##        self.___entry_in.grid(column = 3, row =5, sticky="nesw")
##        self.___text = tk.Text(self,width=100, height = 20)
##        self.___entry_var.set("")
##        self.___text_scrollbar = tk.Scrollbar(self)
##        self.___text.config(yscrollcommand=self.debug_text_scrollbar.set)
##        self.___text_scrollbar.config(command=self.debug_text.yview)
##        self.___text.grid(row=6,column=3,sticky="nesw")
##        self.___text_scrollbar.grid(row=6,column=3,sticky="nesw")
        def connect_command():
            def IPadress():
               filewin = tk.Toplevel(master)
               button = tk.Button(filewin, text="Do nothing button")
               button.pack()

            if self.options_var.get() != "": self.connection_entry_var.set(str(self.options_var.get()))
            if self.autodetect_checkbutton_var.get() == 1: autodetect = True
            else: autodetect = False
            com_device = self.connection_entry_var.get()
            msg = autodetect,com_device
            if self.options_var.get() == "Network":
                IPadress()
            else:
                self.initQueue.put(msg)

        self.scanbutton = tk.Button(self, text='Rescan', command = scan)
        self.scanbutton.grid(column = 3, row = 5, sticky = "e")
        self.connectbutton = tk.Button(self, text='Connect', command= connect_command)
        self.connectbutton.grid(column = 3, row =4, sticky = "w")
        self.disconnectbutton = tk.Button(self, text='Disconnect', command= close_com, state = tk.DISABLED)
        self.disconnectbutton.grid(column = 3, row =4, sticky = "e")
        self.autodetect_checkbutton_var = tk.IntVar()
        if (platform.system() == 'Windows'):self.autodetect_checkbutton_var.set(1)
        else: self.autodetect_checkbutton_var.set(0)
        self.autodetect_checkbutton = tk.Checkbutton(self, text = "Autodetect", variable = self.autodetect_checkbutton_var)
        if (platform.system() == 'Windows'):self.autodetect_checkbutton.grid(column = 3, row = 7)


##        self.withdraw()


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        master.protocol("WM_DELETE_WINDOW", self.endApplication)
        self.master = master

        # Create the queue
        self.received_queue = Queue.Queue()
        self.receivedDebug_queue = Queue.Queue()
        self.send_queue = Queue.Queue()
        self.init_Queue = Queue.Queue()
        self.receive_connected_queue = Queue.Queue()
        self.connected_queue = Queue.Queue()
        self.saveToFile_Queue = Queue.Queue()
        self.logToFile_Queue = Queue.Queue()

        # Set up the GUI part
        def openDebug():
            self.gui_Debug.deiconify()
            self.gui_Debug.lift()
            self.gui_Debug.focus_set()

        def hide_Debug():
            self.gui_Debug.withdraw()
            master.deiconify()

        def openCom():
            self.gui_com.deiconify()
            self.gui_com.lift()
            self.gui_com.focus_set()

        def hide_Com():
            self.gui_com.withdraw()
            master.deiconify()

        self.gui = GuiPart(master, self.received_queue, self.send_queue,
                            self.receive_connected_queue, self.saveToFile_Queue, self.logToFile_Queue,
                            self.endApplication, openDebug, openCom)
        self.gui_Debug = GuiDebug(master, self.receive_connected_queue, self.send_queue)
        self.gui_Debug.protocol("WM_DELETE_WINDOW", hide_Debug)
        self.gui_com = GuiConnect(master, self.init_Queue, self.close_com)
        self.gui_com.protocol("WM_DELETE_WINDOW", hide_Com)
        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = True
        self.connected = False
        self.init_com = True
    	self.threadI = threading.Thread(target=self.initThread)
        self.master.after(1000,self.threadI.start)
        self.threadR = threading.Thread(target=self.receiveThread)
        self.threadS = threading.Thread(target=self.sendThread)
        self.master.after(1000, self.threadR.start)
        self.master.after(1000, self.threadS.start)


        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.master.after(1000,self.periodicCall)



    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        self.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            pass

        self.master.after(100, self.periodicCall)

    def processIncoming(self):
        while self.receivedDebug_queue.qsize():
            try:
                msg = self.receivedDebug_queue.get()
                self.gui_Debug.debug_entry_in_var.set(msg)
                self.gui_Debug.debug_text.insert(tk.END, msg + "\n")
                if self.gui_Debug.autoscroll_checkbutton_var.get() == 1:
                    self.gui_Debug.debug_text.see(tk.END)
            except Queue.Empty:
                    pass
        while self.connected_queue.qsize():
            try:
                msg = self.connected_queue.get()
                if msg == "connected":
                    self.gui_com.connectbutton.configure(state =  tk.DISABLED)
                    self.gui_com.disconnectbutton.configure(state =  tk.NORMAL)
                    self.connected = True
                    self.master.title("ArdumowerDK " + msg)
                elif msg == "disconnected":
                    self.gui_com.connectbutton.configure(state =  tk.NORMAL)
                    self.gui_com.disconnectbutton.configure(state =  tk.DISABLED)
                    self.connected = False
                    self.master.title("ArdumowerDK " + msg)
                else:
                    self.gui_com.connection_entry_var.set(msg)
                    self.master.title("ArdumowerDK Connected: " + msg)
            except Queue.Empty:
                pass
    def initThread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        def scan_comport(com_exclude):
            com_device = ""
            comport = 1
            while com_device == "" and comport <= 50:

                if comport not in com_exclude:
                    try:
                        com_device = serial.Serial("com" + str(comport), baudrate=19200, writeTimeout = 100000)
                        print "Testing com:",comport
                    except:
                        if int(comport) <= 49:
                            comport += 1
##                            print comport
                        else:
                            com_device = ""
                            print "Failed to connect to Device"
                            connected = False
##                            print comport
                            comport ="51"
                else:
                    comport += 1
                    print "Testing com:",comport
##            comport =1
            return com_device, comport


##        print "init"
        com_device = ""
        com = 0
        com_exclude = []
        connected = False
        while self.init_com:
            time.sleep(0.01)

            if self.init_Queue.qsize():
                try:
                        # Check contents of message and do what it says
                        #
                    msg = self.init_Queue.get(0)
                    autodetect, msg = msg

                    if (msg == "disconnect") and autodetect:
                        self.receive_connected_queue.put("disconnected")
                        self.connected_queue.put("disconnected")
                        connected = False
                        try:
                            self.Ardumower.close()
                        except:
                            print "port cannot close"


                    elif autodetect and  (platform.system() == 'Windows'):
                        while com_device == "" and connected == False and com <=49:
                            com_device, com = scan_comport(com_exclude)
                ##            time.sleep(0.1)
                            if com_device != "":
                                com_device.write("{.}")
                                time.sleep(0.5)
                                while com_device.inWaiting() != 0 and connected == False:
                                    muC = com_device.readline()
                                    if muC.find("Ardumower") >= 0:
                                        print"found Ardumower"
                                        self.Ardumower = com_device
                                        ms = muC + "init"
                                        self.received_queue.put(ms)
                                        self.receive_connected_queue.put("connected")
                                        self.send_queue.put("connected")
                                        msg = ""
                                        autodetect = False
                                        com_exclude = []

                                        self.connected_queue.put("connected")
                                        com = "com" + str(com)
                                        self.connected_queue.put(com)
                                        com = 0
                                        connected = True
                                com_device = ""
                            com_exclude.append(com)


                    elif msg != "":
                        com_device = serial.Serial(msg, baudrate=19200, writeTimeout = 10000)
                        if com_device != "":
                            com_device.write("{.}")
                            time.sleep(0.5)
                            while com_device.inWaiting() != 0 and connected == False:
                                muC = com_device.readline()
                                if muC.find("Ardumower") >= 0:
                                    print"found Ardumower"
                                    self.Ardumower = com_device
                                    ms = muC + "init"
                                    self.receive_connected_queue.put("connected")
                                    self.send_queue.put("connected")
                                    self.received_queue.put(ms)
                                    msg = ""
                                    self.connected_queue.put("connected")
                                    connected = True
##                                else: print "Failed to connect to Device"

                except Queue.Empty:
                    pass
##        if not self.running:
##            self.threadR.start()
##            self.threadS.start()

    def receiveThread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        msg = ""
        connected = False
        sheepReply_checkbutton_var = False
        dataPlot_checkbutton_var = False
        settings_toFile = False
        logToFile = False
        while self.running:
            time.sleep(0.01)
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following 2 lines with the real
            # thing.
            if  self.receive_connected_queue.qsize():
                try:
                        # Check contents of message and do what it says
                    msg = self.receive_connected_queue.get(0)
##                    print msg
                    if msg == "connected":
                        connected = True
                        mower = self.Ardumower

                    elif msg == "disconnected": connected = False
                    elif msg == "Sheep Debug": sheepReply_checkbutton_var = True
                    elif msg == "Sheep noDebug": sheepReply_checkbutton_var = False
                    elif msg == "Data Debug": dataPlot_checkbutton_var = True
                    elif msg == "Data noDebug": dataPlot_checkbutton_var = False
                    elif msg == "settings_toFile": settings_toFile = True
                    elif msg == "not_settingsToFile": settings_toFile = False
                    elif msg == "log": logToFile = True
                    elif msg == "no log": logToFile = False
                    msg = ""

                except Queue.Empty:
                    pass


            if connected and  mower.inWaiting() != 0:
                try:

                    msg += mower.readline()


                    if (msg.find("|") == -1) and (msg.find(",") == -1) and (msg.find("{") == -1) and (msg.find("}") == -1):
                        self.receivedDebug_queue.put("Sheep debug: " + msg)
                        msg = ""
                    elif not msg.find("{")>= 0:
                        if not logToFile: self.received_queue.put(msg)
                        else: self.logToFile_Queue.put(msg)
                        if dataPlot_checkbutton_var == True: self.receivedDebug_queue.put("Plot data: " + msg)
                        msg = ""

                    elif msg.find("}")>= 0:
                        if settings_toFile: self.saveToFile_Queue.put(msg)
##                        elif logToFile: self.logToFile_Queue.put(msg)
                        else: self.received_queue.put(msg)

                        if sheepReply_checkbutton_var == True: self.receivedDebug_queue.put("Sheep : " + msg)
                        msg = ""
                except serial.SerialException:
                    self.connected_queue.put("disconnected")
                    pass


        if self.running == False:
            pass
##            msg = "{.Ardumower (Ardumower)|r~Commands|n~Manual|s~Settings|in~Info|c~Test compass|m1~Log sensors|yp~Plot|y4~Error counters|y9~ADC calibration}init"
##            self.received_queue.put(msg)
####            msg = "{.Commands`5000|ro~OFF|ra~Auto mode|rc~RC mode|rm~Mowing is OFF|rp~Pattern is RAND|rh~Home|rk~Track|rs~State is OFF |rr~Auto rotate is 0.00|r1~User switch 1 is OFF|r2~User switch 2 is OFF|r3~User switch 3 is OFF}"
######            msg = "|nl~Left|nr~Right|nf~Forward|nb~Reverse|nm~Mow is OFF}"
######            msg = "{.Mow`1000|o00~Overload Counter 0|o01~Power in Watt 0.00|o11~current in mA 0.00|o02~Power max `1000`1000`0~ ~0.1|o03~calibrate mow motor  `0`3000`0~ ~1|o04~Speed 0.00|o05~Speed max `255`255`0~ ~1|o06~Modulate NO|o07~RPM 0|o08~RPM set `3300`4500`0~ ~1|o09p~RPM_P `0`100`0~ ~0.01|o09i~RPM_I `1`100`0~ ~0.01|o09d~RPM_D `1`100`0~ ~0.01|o10~Testing is OFF|o04~for config file: motorMowSenseScale:15.30}"
##            time.sleep(5)
##            msg = "{.Plot|y7~Sensors|y5~Sensor counters|y3~IMU|y6~Perimeter|y8~GPS|y1~Battery|y2~Odometry2D|y11~Motor control|y10~GPS2D}"
##            self.received_queue.put(msg)
##            msg ="{=Sensors`300|time s`0|state`1|motL`2|motR`3|motM`4|sonL`5|sonC`6|sonR`7|peri`8|lawn`9|rain`10|dropL`11|dropR`12}"
##            time.sleep(5)
##            self.received_queue.put(msg)
##            for i in range(1000):
##                time.sleep(0.5)
##                if i%2 == 0 :
##                    msg = str(i)+",12,2,0.02,0.10,100,2507,5,1,3,27,25000,0"
####                    print "data:", msg
##                if i%2 != 0:
##                    msg = "Debug string " + str(i)
####                    print "dbug:", msg
##
##                if (msg.find("|") == -1) and (msg.find(",") == -1) and (msg.find("{") == -1) and (msg.find("}") == -1):
##                    self.receivedDebug_queue.put(msg)
##                    msg = ""
##                elif not msg.find("{")>= 0:
##                    self.received_queue.put(msg)
####                    print msg
##                    msg = ""
##                elif msg.find("}")>= 0:
##                    self.received_queue.put(msg)
####                    print msg
##                    msg = ""

    def sendThread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
        connected = False
        sheepSent_checkbutton_var = False
        while self.running:
            time.sleep(0.01)
            if  self.send_queue.qsize():
                try:
                        # Check contents of message and do what it says
                        #
                    msg = self.send_queue.get(0)
##                    print msg
                    if msg == "connected":
                        connected = True
                        mower = self.Ardumower
                    elif msg == "Sent Debug": sheepSent_checkbutton_var = True
                    elif msg == "Sent noDebug": sheepSent_checkbutton_var = False
                    elif msg == "disconnected": connected = False


                    elif connected:
                        try:
                            mower.write("{" + msg + "}" + "\n")
                            if sheepSent_checkbutton_var == True: self.receivedDebug_queue.put("DK: "+ msg)
                        except serial.SerialException:
                            self.connected_queue.put("disconnected")
                            pass
                except Queue.Empty:
                    pass
##        while self.running == False:
##            if self.send_queue.qsize():
##                try:
##                        # Check contents of message and do what it says
##                        #
##                    msg = self.send_queue.get(0)
##                    print msg
##                except Queue.Empty:
##                    pass


    def endApplication(self):

        if self.running:
            if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
                self.running = False
                self.init_com = False
                self.master.after(100, self.close_com)
                self.master.after(1000, self.master.destroy)

##                self.master.after(1000, sys.exit)
        else:
            self.master.destroy()

    def close_com(self):
        if self.connected:
            autodetect = True
            ms = "disconnect"
            msg = autodetect, ms
            if self.init_com: self.init_Queue.put(msg)
            else: self.Ardumower.close()

rand = random.Random()
root = tk.Tk()
if (platform.system() == 'Windows'):
    root.iconbitmap(default='Toy.ico')
else:
    root.iconbitmap('@Toy.xbm')
root.title('ArdumowerDK')
root.geometry('+50+10')
client = ThreadedClient(root)
root.mainloop()