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

PING_FREQUENCY = 1  # seconds
stelgewicht = '-'
andergewicht = 'Ander gewicht: {custweight}'.format(custweight=stelgewicht)
gewicht = 0
emptyweight = 0
ports = list_ports.comports()


class MyIndicator:
    ser = Serial(
        # port='/dev/ttyUSB9',
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

    def VulGewichtIn(self):
        self.popup = gtk.Dialog(title='Gewicht')
        self.popup.entry = gtk.Entry()
        self.popup.entry.set_text(
            '{custweight}'.format(custweight=stelgewicht))
        self.popup.vbox.pack_start(self.popup.entry, True, True, 0)

        self.popup.cancel = gtk.Button("Cancel")
        self.popup.cancel.connect("clicked", self.on_cancel_clicked)
        self.popup.vbox.pack_start(self.popup.cancel, True, True, 0)

        self.popup.ok = gtk.Button("Ok")
        self.popup.ok.connect("clicked", self.on_ok_clicked)
        self.popup.vbox.pack_start(self.popup.ok, True, True, 0)
        self.popup.show_all()

    def on_cancel_clicked(self, button):
        self.popup.destroy()

    def on_ok_clicked(self, button):
        global emptyweight
        global stelgewicht
        stelgewicht = float(self.popup.entry.get_text())
        andergewicht = 'Ander gewicht: {custweight}'.format(
            custweight=stelgewicht)
        self.setcustomweight.get_child().set_text(andergewicht)
        self.popup.destroy()
        emptyweight = stelgewicht
        self.writeArduino()
        self.savefile("setcustomweight")

    def on_button_toggled(self, button, name, kg):
        global emptyweight

        if button.get_active():
            if name == "VulGewichtIn":
                emptyweight = float(self.VulGewichtIn())
            else:
                emptyweight = kg
                self.writeArduino()
                self.savefile(name)

    def receiving(self, ser):
        global last_received
        global gewicht
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
                    gewicht = float(last_received) / 10
                    self.menuWeight.get_child().set_text('Het fust weegt {printWeight} Kg'.format(
                        printWeight=gewicht + float(emptyweight)))
                    bier = '{nrbier}L'.format(nrbier=gewicht)
                    self.ind.set_label(bier)
                    return True
                    break

    def writeArduino(self, *button):
        if self.suboptionsNixie.get_active():
            nixies = 1
        else:
            nixies = 0
        sendserial = float(emptyweight) * 100 + nixies
        print(sendserial)
        ser.write(str(sendserial))

    def savefile(self, name):
        global stelgewicht
        textfile = open('.savefile', 'w')
        textfile.write(
            'self.{beerbutton}.set_active(True)'.format(beerbutton=name) + '\n')
        textfile.write('{weightprint}'.format(weightprint=emptyweight) + '\n')
        textfile.write('self.suboptionsNixie.set_active({nixieson})'.format(
            nixieson=self.suboptionsNixie.get_active()) + '\n')
        if name == "setcustomweight":
            textfile.write('{weightprint}'.format(weightprint=emptyweight))
        else:
            textfile.write('{weightprint}'.format(weightprint=stelgewicht))
        # you can omit in most cases as the destructor will call if
        textfile.close()

    def loadfile(self):
        global stelgewicht
        global emptyweight
        textfile = open('.savefile', 'r')
        lines = textfile.readlines()
        textfile.close()
        exec(lines[0].rstrip('\n'))  # Togle saved beer button
        emptyweight = float(lines[1].rstrip('\n'))
        # exec(lines[2]) #Toggle saved nixie status
        stelgewicht = lines[3].rstrip('\n')
        andergewicht = 'Ander gewicht: {custweight}'.format(
            custweight=stelgewicht)
        self.setcustomweight.get_child().set_text(andergewicht)

    def createPortList(self, portName):
        portName = portName[0]
        if "ttyS10" in portName:
            self.portName = gtk.RadioMenuItem(label=str(portName))
            self.menuoptions.append(self.portName)
            self.portName.connect("activate", self.setPort, portName)

    def setPort(self, button, portName):
        self.ser.port = portName
        print("Set serial to port: ", portName)

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
            'Het fust weegt {printWeight} Kg'.format(printWeight=gewicht + emptyweight))
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

        self.submenuKeg = gtk.RadioMenuItem(label='Keg')
        self.submenuGrolsh = gtk.RadioMenuItem(
            group=self.submenuKeg, label='Grolsh')
        self.submenuHeineken = gtk.RadioMenuItem(
            group=self.submenuKeg, label='Heineken')
        self.submenuUttinger = gtk.RadioMenuItem(
            group=self.submenuKeg, label='Uttinger')
        self.submenu30L_Uttinger = gtk.RadioMenuItem(
            group=self.submenuKeg, label='Uttinger 30L')
        self.setcustomweight = gtk.RadioMenuItem(
            group=self.submenuKeg, label=andergewicht)

        self.suboptionsNixie = gtk.CheckMenuItem("Nixies")
        self.suboptionsLeds = gtk.CheckMenuItem("LEDS")

        self.menu.append(self.menuWeight)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(menuItemBeer)
        self.menu.append(menuItemOptions)
        self.menu.append(menuItemQuit)

        self.menubeer.append(self.submenuKeg)  # append to the submenu menubeer
        self.menubeer.append(self.submenuGrolsh)
        self.menubeer.append(self.submenuHeineken)
        self.menubeer.append(self.submenuUttinger)
        self.menubeer.append(self.submenu30L_Uttinger)
        self.menubeer.append(gtk.SeparatorMenuItem())
        self.menubeer.append(self.setcustomweight)

        self.menuoptions.append(self.suboptionsNixie)
        self.menuoptions.append(self.suboptionsLeds)

        menuItemQuit.connect('activate', self.quit, "quit")

        self.loadfile()

        self.submenuKeg.connect(
            "toggled", self.on_button_toggled, "submenuKeg", 15)
        self.submenuGrolsh.connect(
            "toggled", self.on_button_toggled, "submenuGrolsh", 14.3)
        self.submenuHeineken.connect(
            "toggled", self.on_button_toggled, "submenuHeineken", 17)
        self.submenuUttinger.connect(
            "toggled", self.on_button_toggled, "submenuUttinger", 19)
        self.submenu30L_Uttinger.connect(
            "toggled", self.on_button_toggled, "submenu30L_Uttinger", 12)
        self.setcustomweight.connect(
            "activate", self.on_button_toggled, "VulGewichtIn", 2)

        self.suboptionsNixie.connect("activate", self.writeArduino)
        self.suboptionsLeds.connect("activate", self.writeArduino)

        # self.createPortList('ttyUSB0')
        [self.createPortList(x) for x in ports]

        self.menu.show_all()

        # Add constructed menu as indicator menu
        self.ind.set_menu(self.menu)
        # glib.timeout_add(1000, self.receiving, ser)


if True:
    bier = '{nrbier}L'.format(nrbier=gewicht)
    indicator = MyIndicator()
    # indicator.loadfile()
    indicator.ind.set_label(bier)
    gtk.main()