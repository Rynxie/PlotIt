#!/usr/bin/env python3

import serial
import serial.tools.list_ports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas


import os
import time
import csv
from random import random


os.environ["GTK_THEME"] = os.getenv("GTK_THEME", "Adwaita:dark")



def get_gtk_theme_colors():
    win = Gtk.Window()
    context = win.get_style_context()

 
    bg_color = context.lookup_color("theme_bg_color")[1] or Gdk.RGBA(1, 1, 1, 1)
    fg_color = context.lookup_color("theme_fg_color")[1] or Gdk.RGBA(0, 0, 0, 1)
    accent_color = context.lookup_color("theme_selected_bg_color")[1] or Gdk.RGBA(1, 0, 0, 1)

   
    return [
        (bg_color.red, bg_color.green, bg_color.blue),
        (fg_color.red, fg_color.green, fg_color.blue),
        (accent_color.red, accent_color.green, accent_color.blue)
    ]

class MainWin(Gtk.Window):
    def __init__(self, portName, baudrate, log):
        super().__init__(title="Plot It!")
        self.set_default_size(800, 600)
        self.connect("destroy", Gtk.main_quit)

        theme = get_gtk_theme_colors()
        print(theme)
        
        self.portName = portName
        self.baudrate = baudrate
        self.log      = log
        self.logPath  = f"./log/{int(random() * 1000000)}.csv"

        if self.log is True:
            os.makedirs(os.path.dirname(self.logPath), exist_ok=True)
            self.file = open(self.logPath , mode='a', newline='', encoding='utf-8')
            self.writer = csv.writer(self.file)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        

        self.box.set_margin_top(20)
        self.box.set_margin_bottom(20) 
        self.box.set_margin_start(20)  
        self.box.set_margin_end(20)    
        self.add(self.box)

        self.fig, self.ax = plt.subplots()
        self.xdata, self.ydata = [], []
        self.line, = self.ax.plot(self.xdata, self.ydata, 'r-',color=theme[2])
        self.ax.set_facecolor(color=theme[0])
        self.fig.set_facecolor(color=theme[0])
        for spine in self.ax.spines.values():
            spine.set_color(theme[1])
        
        self.ax.tick_params(axis='x', colors=theme[2])  
        self.ax.tick_params(axis='y', colors=theme[2])   
        
        self.canvas = FigureCanvas(self.fig)
        
        self.box.pack_start(self.canvas,True,True,0)
        self.canvas.show()
        
        innerBox = Gtk.Box(spacing=6)
        leftLabel = Gtk.Label(label=f"Plotting the {self.portName}")
        leftLabel.set_halign(Gtk.Align.START)
        innerBox.pack_start(leftLabel, True, True,0)

        rightLabel = Gtk.Label(label=f"Logging into the {self.logPath}")
        if self.log is False:
            rightLabel.set_label("Not Logging!")
        rightLabel.set_halign(Gtk.Align.END)
        innerBox.pack_start(rightLabel, True, True,0)

        self.box.pack_start(innerBox, False, False, 0)



        self.port = serial.Serial(self.portName, self.baudrate)
       
        GLib.idle_add(self.updateGraph)


    def getData(self):
   
        try:
            newX = len(self.xdata)
            newY = float(self.port.readline())
        except:
            newX = self.xdata[len(self.xdata) - 1] if self.xdata else 0
            newY = self.ydata[len(self.ydata) - 1] if self.ydata else 0
        return newX, newY

    def updateGraph(self):
        newX, newY = self.getData()
        self.xdata.append(newX)
        self.ydata.append(newY)

        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        
        if self.log is True:
            self.writer.writerow([newY])
            self.file.flush()
        time.sleep(0.050);
        return True
    
class WelcomeWin(Gtk.Window):
    def __init__(self):
        super().__init__(title="Plot It!")
        self.set_default_size(200, 300)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)

        box.set_margin_top(20)    
        box.set_margin_bottom(20)  
        box.set_margin_start(20)   
        box.set_margin_end(20)     
        
        self.add(box)

        portsRaw = serial.tools.list_ports.comports()
        
        box.pack_start(Gtk.Label(label="Plot It!"),False,False,0)
        
        self.combo = Gtk.ComboBoxText()

        for port in portsRaw:
          
            if port.name[3:6] == "ACM" or port.name[3:6] == "USB":
                self.combo.append_text(port.name)
                print("matched\n")
        
        self.combo.set_active(0)

        box.pack_start(self.combo, False, False, 0)

        self.baudrateInput = Gtk.Entry()
        self.baudrateInput.set_placeholder_text("Baudrate")

        box.pack_start(self.baudrateInput, False, False, 0)

        innerBox = Gtk.Box(spacing=6)

        innerBox.pack_start(Gtk.Label(label="Create a CSV log?"), True, True, 0)

        self.checkBox = Gtk.CheckButton()

        innerBox.pack_start(self.checkBox, True, True, 0)

        box.pack_start(innerBox, False, False, 0)

        self.button = Gtk.Button(label="Plot")

        self.button.connect("clicked", self.on_plot_clicked)
        
        box.pack_start(self.button, False, False, 0)

    def on_plot_clicked(self, widget):

        selectedPort = "/dev/" + self.combo.get_active_text()
        baudrate = int(self.baudrateInput.get_text())
        log      = self.checkBox.get_active()

        print(selectedPort)
        print(baudrate)
        print(log)
         
        plotWin = MainWin(selectedPort,baudrate,log)
        self.destroy()
        plotWin.show_all()
        
    



if __name__ == "__main__":
    pencere = WelcomeWin()
    pencere.show_all()
    Gtk.main()

