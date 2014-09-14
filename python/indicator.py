#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import serial
import time
ser=serial.Serial(0)
#port=ser.name
have_appindicator = True
try:
    import appindicator
except:
    have_appindicator = False

PING_FREQUENCY = 1 # seconds
stelgewicht = '-'
andergewicht = 'Ander gewicht: {custweight}'.format(custweight = stelgewicht)
gewicht = 0
emptyweight = 0

class MyIndicator:

    ## functions to handle events    
    def quit(self, widget, data=None):
        gtk.main_quit()
        ser.close()
        
        
        
    def VulGewichtIn(self):

        self.popup = gtk.Dialog(title='Gewicht')
        self.popup.entry = gtk.Entry()
        self.popup.entry.set_text('{custweight}'.format(custweight = stelgewicht))
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
        self.readArduino() 
    
    def on_ok_clicked(self, button):
        global emptyweight
        global stelgewicht
        stelgewicht = float(self.popup.entry.get_text())
        andergewicht = 'Ander gewicht: {custweight}'.format(custweight = stelgewicht)
        self.setcustomweight.get_child().set_text(andergewicht)
        self.popup.destroy()
        emptyweight = stelgewicht
        self.writeArduino()
        self.savefile("setcustomweight")
        self.readArduino()        

    def on_button_toggled(self, button, name, kg):
        global emptyweight
        
        if button.get_active():
            if name=="VulGewichtIn":
                emptyweight = self.VulGewichtIn()                              
            else:    
                emptyweight = kg
                self.savefile(name)                                         

    def readArduino(self):
        global gewicht
        # while True: 
        #     gewicht = ser.readline()
        gewicht = gewicht+0.1
        print(gewicht)
        self.menuWeight.get_child().set_text('Het fust weegt {printWeight} Kg'.format(printWeight = gewicht + emptyweight))
        bier = '{nrbier}L'.format(nrbier = gewicht)
        self.ind.set_label(bier)
        gtk.timeout_add(PING_FREQUENCY * 1000, self.readArduino)

    def writeArduino(self, *button):
        #ser.write(emptyweight)
        print(emptyweight)
        #ser.write(suboptionsLed.get_active())
        print(self.suboptionsLed.get_active())
        #ser.write(suboptionsNixie.get_active())
        print(self.suboptionsNixie.get_active())
               

    def savefile(self, name):
        global stelgewicht
        savefile = open('.savefile','w')
        savefile.write('self.{beerbutton}.set_active(True)'.format(beerbutton=name)+'\n')

        savefile.write('{weightprint}'.format(weightprint=emptyweight)+'\n')
        savefile.write('self.suboptionsLed.set_active({ledson})'.format(ledson=self.suboptionsLed.get_active())+'\n')
        savefile.write('self.suboptionsNixie.set_active({nixieson})'.format(nixieson=self.suboptionsNixie.get_active())+'\n')
        if name == "setcustomweight":
            savefile.write('{weightprint}'.format(weightprint=emptyweight))
        else:
            savefile.write('{weightprint}'.format(weightprint=stelgewicht))
        savefile.close() # you can omit in most cases as the destructor will call if
        
    def loadfile(self):
        global stelgewicht
        global emptyweight
        savefile = open('.savefile', 'r')
        lines=savefile.readlines()
        savefile.close()
        exec(lines[0].rstrip('\n')) #Togle saved beer button
        emptyweight = float(lines[1].rstrip('\n'))
        exec(lines[2].rstrip('\n')) #Toggle saved led status
        exec(lines[3]) #Toggle saved nixie status
        stelgewicht = lines[4].rstrip('\n')
        andergewicht = 'Ander gewicht: {custweight}'.format(custweight = stelgewicht)
        self.setcustomweight.get_child().set_text(andergewicht)

        

             
    ## Initialise
    def __init__(self):        
        
        ## Create appindicator object
        if have_appindicator:
            self.ind = appindicator.Indicator ("example-simple-client",
                        "indicator-messages",
                        appindicator.CATEGORY_APPLICATION_STATUS)
            self.ind.set_status (appindicator.STATUS_ACTIVE)
            self.ind.set_icon("/home/anne/Dropbox/Arduino/weegschaal/python/biertje.svg")            
        else:
            self.ind = gtk.status_icon_new_from_stock(gtk.STOCK_HOME)
        
        ## Create menu object
        self.menu = gtk.Menu()    ## create the main menu item
        self.menuWeight = gtk.MenuItem('Het fust weegt {printWeight} Kg'.format(printWeight = gewicht + emptyweight))
        self.menuWeight.set_sensitive(False)
        menuItemBeer = gtk.MenuItem('Beer')
        menuItemOptions = gtk.MenuItem('Options')
        menuItemQuit = gtk.MenuItem('Quit')


        self.menubeer = gtk.Menu() ## Create second menu for the submenu
        self.menuoptions = gtk.Menu() ## make options allso a menu
        menuItemBeer.set_submenu(self.menubeer)	## Make MenuItemBeer submenuable
        menuItemOptions.set_submenu(self.menuoptions) ## make the menuoptions a submenu of itemoptions
                
        self.submenuKeg = gtk.RadioMenuItem(label='Keg')
        self.submenuGrolsh = gtk.RadioMenuItem(group=self.submenuKeg, label='Grolsh')
        self.submenuHeineken = gtk.RadioMenuItem(group=self.submenuKeg, label='Heineken')
        self.submenuUttinger = gtk.RadioMenuItem(group=self.submenuKeg, label='Uttinger')
        self.submenu30L_Uttinger = gtk.RadioMenuItem(group=self.submenuKeg, label='30L Uttinger')
        self.setcustomweight = gtk.RadioMenuItem(group=self.submenuKeg, label=andergewicht)
        self.suboptionsLed = gtk.CheckMenuItem("Backlight LEDs")
        self.suboptionsNixie = gtk.CheckMenuItem("Nixies")
        
        self.menu.append(self.menuWeight)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(menuItemBeer)
        self.menu.append(menuItemOptions)
        self.menu.append(menuItemQuit)
        
        self.menubeer.append(self.submenuKeg)	## append to the submenu menubeer
        self.menubeer.append(self.submenuGrolsh)
        self.menubeer.append(self.submenuHeineken)
        self.menubeer.append(self.submenuUttinger)
        self.menubeer.append(self.submenu30L_Uttinger)
        self.menubeer.append(gtk.SeparatorMenuItem())
        self.menubeer.append(self.setcustomweight)
        
        self.menuoptions.append(self.suboptionsLed)
        self.menuoptions.append(self.suboptionsNixie)

        menuItemQuit.connect('activate', self.quit, "quit")

        self.loadfile()

        self.submenuKeg.connect("toggled", self.on_button_toggled, "submenuKeg", 15)
        self.submenuGrolsh.connect("toggled", self.on_button_toggled, "submenuGrolsh", 14.3)
        self.submenuHeineken.connect("toggled", self.on_button_toggled, "submenuHeineken", 17)
        self.submenuUttinger.connect("toggled", self.on_button_toggled, "submenuUttinger", 19)
        self.submenu30L_Uttinger.connect("toggled", self.on_button_toggled, "submenu30L_Uttinger", 12)
        self.setcustomweight.connect("activate", self.on_button_toggled, "VulGewichtIn", 2)

        self.suboptionsLed.connect("activate", self.writeArduino)
        self.suboptionsNixie.connect("activate", self.writeArduino)
        
        ## Show all in menu (instead of calling .show() for each item)
        self.menu.show_all()
        
        ## Add constructed menu as indicator menu
        self.ind.set_menu(self.menu)   
        self.readArduino() 
    def main(self):
        gtk.main()


if __name__ == "__main__":
   bier = '{nrbier}L'.format(nrbier = gewicht)
   indicator = MyIndicator()
   indicator.ind.set_label(bier)
   indicator.main()
   


