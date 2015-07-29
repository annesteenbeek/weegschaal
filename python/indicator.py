#!/usr/bin/env python

import sys
import pygtk
pygtk.require('2.0')
import gtk
have_appindicator = True
try:
    import appindicator  # apt-get install python-appindicator
except:
    have_appindicator = False
from serial import *       # pip install pyserial
import time
import glib
from serial.tools import list_ports
import json

PING_FREQUENCY = 1  # seconds


class MyIndicator:
    ports = []
    gewicht = 0
    emptyweight = 0
    color = gtk.gdk.Color('#FFFFFF')
    selectedKeg = "grolsch"
    portdict = {}

    ser = Serial(
        baudrate=9600,
        bytesize=EIGHTBITS,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
        timeout=None,
        xonxoff=0,
        rtscts=0,
        interCharTimeout=None
    )

    # functions to handle events
    def quit(self, widget, data=None):
        gtk.main_quit()

    def colorSelector(self, widget):
        handled = False
        # Check if we've received a button pressed event
        if True:
            handled = True

            # Create color selection dialog
            if self.colorseldlg == None:
                self.colorseldlg = gtk.ColorSelectionDialog(
                    "Select background color")

            # Get the ColorSelection widget
            colorsel = self.colorseldlg.colorsel

            colorsel.set_previous_color(self.color)
            colorsel.set_current_color(self.color)
            colorsel.set_has_palette(True)

            # Connect to the "color_changed" signal
            self.color = self.colorseldlg.colorsel.get_current_color()
            colorsel.connect("color_changed", self.writeArduino)
            # Show the dialog
            response = self.colorseldlg.run()

            if response -- gtk.RESPONSE_OK:
                self.color = colorsel.get_current_color()
            else:
                self.drawingarea.modify_bg(gtk.STATE_NORMAL, self.color)

            self.colorseldlg.hide()

        return handled

    def kegSelect(self, button, name, kg):
        if button.get_active():
            self.selectedKeg = name
            self.emptyweight = kg
            self.writeArduino()

    def receiving(self, ser):
        global last_received
        buffer = ''
        ser.flushInput()
        while True:
            buffer = buffer + ser.read(ser.inWaiting())
            if '\n' in buffer:
                # Guaranteed to have at least 2 entries
                lines = buffer.split('\n')
                last_received = lines[-2]
                # If the Arduino sends lots of empty lines, you'll lose the
                # last filled line, so you could make the above statement conditional
                # like so: if lines[-2]: last_received = lines[-2]
                buffer = lines[-1]
                if last_received != '\r' and last_received != '\n' and last_received != '':
                    self.gewicht = float(last_received) / 10
                    self.menuWeight.get_child().set_text('Het fust weegt {printWeight} Kg'.format(
                        printWeight=self.gewicht + float(self.emptyweight)))
                    bier = '{nrbier}L'.format(nrbier=self.gewicht)
                    self.ind.set_label(bier)
                    return True
                    break

    def writeArduino(self, *button):
        if bool(self.ser.port):
            if self.colorseldlg != None:
                self.color = self.colorseldlg.colorsel.get_current_color()
            color = [gtk.gdk.Color.to_string(self.color)[i] for i in [1, 2, 5, 6, 9, 10]]
            color = ''.join(color)
            # print(gtk.gdk.Color.to_string(color))
            print(color)
            self.ser.write(color)
        self.savefile()

    def savefile(self):
        data = {"ledcolor": gtk.gdk.Color.to_string(self.color),
                "ledson": self.suboptionsLeds.get_active(),
                "nixieson": self.suboptionsNixie.get_active(),
                "kegtype": self.selectedKeg,
                "usbport": self.ser.port}

        with open('.savefile.json', "w+") as outfile:
            json.dump(data, outfile)

    def loadfile(self):
        with open('.savefile.json', "r") as infile:
            data = json.load(infile)

        self.color = gtk.gdk.Color(data["ledcolor"])
        self.suboptionsLeds.set_active(data["ledson"])
        self.suboptionsNixie.set_active(data["nixieson"])
        self.ser.port = data["usbport"]
        self.selectedKeg = data["kegtype"]

        self.beerdict[self.selectedKeg].activate()
        # self.createPortList()

    def createPortList(self):
        for portname in self.portdict.keys():
            self.menuoptions.remove(self.portdict[portname])
        self.portdict = {}

        self.ports = []
        for x in list_ports.comports():
            portName = x[0]
            if 'USB' in portName:
                self.ports.append(portName)
                self.portdict[portName] = gtk.RadioMenuItem(label=str(portName))
                self.menuoptions.append(self.portdict[portName])
                self.portdict[portName].connect("activate", self.setPort, portName)
                if self.ser.port not in self.ports:
                    self.ser.port = self.ports[0]
                    self.portdict[self.ser.port].activate()
        if len(self.ports) == 0:
            self.portdict["nousb"] = gtk.MenuItem('Geen usb gevonden')
            self.menuoptions.append(self.portdict["nousb"])
            self.portdict["nousb"].set_sensitive(False)

    def setPort(self, button, portName):
        self.ser.port = portName
        self.ser.open()
        print("Set serial to port: ", portName)

    def createBeerList(self):
        self.beerdict = {}
        with open('fustlijst.json', "r") as infile:
            self.beerlist = json.load(infile)

            beer = self.beerlist.keys()[0]
            weight = self.beerlist[beer]
            self.beerdict[beer] = gtk.RadioMenuItem(label=beer)
            self.menubeer.append(self.beerdict[beer])
            self.beerdict[beer].connect("activate", self.kegSelect, beer, weight)
            groupname = self.beerdict[beer]

        for beer in self.beerlist.keys()[1:]:
            weight = self.beerlist[beer]
            self.beerdict[beer] = gtk.RadioMenuItem(group=groupname, label=beer)
            self.menubeer.append(self.beerdict[beer])
            self.beerdict[beer].connect("activate", self.kegSelect, beer, weight)
        self.menubeer.append(gtk.SeparatorMenuItem())

    # Initialise
    def __init__(self):
        # Create appindicator object
        if have_appindicator:
            self.ind = appindicator.Indicator("example-simple-client",
                                              "indicator-messages",
                                              appindicator.CATEGORY_APPLICATION_STATUS)
            self.ind.set_status(appindicator.STATUS_ACTIVE)
            self.ind.set_icon(
                "/home/anne/Dropbox/Arduino/weegschaal/python/biertje.svg")
        else:
            self.ind = gtk.status_icon_new_from_stock(gtk.STOCK_HOME)

        # Create menu object
        self.menu = gtk.Menu()  # create the main menu item
        self.menuWeight = gtk.MenuItem(
            'Het fust weegt {printWeight} Kg'.
            format(printWeight=self.gewicht + self.emptyweight))

        self.menuWeight.set_sensitive(False)
        menuItemBeer = gtk.MenuItem('Beer')
        menuItemOptions = gtk.MenuItem('Options')
        menuItemQuit = gtk.MenuItem('Quit')

        self.menubeer = gtk.Menu()  # Create second menu for the submenu
        self.menuoptions = gtk.Menu()  # make options allso a menu
        # Make MenuItemBeer submenuable
        menuItemBeer.set_submenu(self.menubeer)
        # make the menuoptions a submenu of itemoptions
        menuItemOptions.set_submenu(self.menuoptions)

        self.suboptionsNixie = gtk.CheckMenuItem("Nixies")
        self.suboptionsLeds = gtk.CheckMenuItem("LEDs")
        self.suboptionsColor = gtk.MenuItem("Select LED color")

        self.menu.append(self.menuWeight)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(menuItemBeer)
        self.menu.append(menuItemOptions)
        self.menu.append(menuItemQuit)

        self.menuoptions.append(self.suboptionsNixie)
        self.menuoptions.append(self.suboptionsLeds)
        self.menuoptions.append(self.suboptionsColor)

        menuItemQuit.connect('activate', self.quit, "quit")

        self.createBeerList()
        self.createPortList()

        self.suboptionsNixie.connect("activate", self.writeArduino)
        self.suboptionsLeds.connect("activate", self.writeArduino)
        self.colorseldlg = None
        self.suboptionsColor.connect("activate", self.colorSelector)

        self.loadfile()

        self.menu.show_all()

        # Add constructed menu as indicator menu
        self.ind.set_menu(self.menu)
        # glib.timeout_add(1000, self.receiving, ser)


if True:
    bier = '{nrbier}L'.format(nrbier=MyIndicator.gewicht)
    indicator = MyIndicator()
    # indicator.loadfile()
    indicator.ind.set_label(bier)
    gtk.main()
