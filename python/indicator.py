import pygtk
pygtk.require('2.0')
import gtk
import serial
#ser=serial.Serial(0)
#port=ser.name
have_appindicator = True
try:
    import appindicator
except:
    have_appindicator = False

PING_FREQUENCY = 1 # seconds
stelgewicht = '-'
andergewicht = 'Ander gewicht: {custweight}'.format(custweight = stelgewicht)
weight = 10

class MyIndicator:

    ## functions to handle events    
    def quit(self, widget, data=None):
        gtk.main_quit()
        ser.close()
        
        
    def VulGewichtIn(self):

        self.popup = gtk.Dialog(title='Gewicht')
        self.popup.entry = gtk.Entry()
        self.popup.entry.set_text("Gewicht")
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
        stelgewicht = self.popup.entry.get_text()
        andergewicht = 'Ander gewicht: {custweight}'.format(custweight = stelgewicht)
        self.setcustomweight.get_child().set_text(andergewicht)
        self.popup.destroy()
        return stelgewicht

    def on_button_toggled(self, button, name, kg):
        if button.get_active():
            if name=="VulGewichtIn":
                emptyweight=self.VulGewichtIn()
            else:    
                emptyweight = kg
        else:
            state = "off"
        
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
        menuWeight = gtk.MenuItem('Het fust weegt {printWeight} Kg'.format(printWeight = weight))
        menuWeight.set_sensitive(False)
        menuItemBeer = gtk.MenuItem('Beer')
        menuItemOptions = gtk.MenuItem('Options')
        menuItemQuit = gtk.MenuItem('Quit')


        self.menubeer = gtk.Menu() ## Create second menu for the submenu
        self.menuoptions = gtk.Menu() ## make options allso a menu
        menuItemBeer.set_submenu(self.menubeer)	## Make MenuItemBeer submenuable
        menuItemOptions.set_submenu(self.menuoptions) ## make the menuoptions a submenu of itemoptions
                
        submenuKeg = gtk.RadioMenuItem(label='Keg')
        submenuGrolsh = gtk.RadioMenuItem(group=submenuKeg, label='Grolsh')
        submenuHeineken = gtk.RadioMenuItem(group=submenuKeg, label='Heineken')
        submenuUttinger = gtk.RadioMenuItem(group=submenuKeg, label='Uttinger')
        submenu30L_Uttinger = gtk.RadioMenuItem(group=submenuKeg, label='30L Uttinger')
        self.setcustomweight = gtk.RadioMenuItem(group=submenuKeg, label=andergewicht)
        suboptionsLed = gtk.CheckMenuItem("Backlight LEDs")
        suboptionsNixie = gtk.CheckMenuItem("Nixies")
        
        self.menu.append(menuWeight)
        self.menu.append(gtk.SeparatorMenuItem())
        self.menu.append(menuItemBeer)
        self.menu.append(menuItemOptions)
        self.menu.append(menuItemQuit)
        
        self.menubeer.append(submenuKeg)	## append to the submenu menubeer
        self.menubeer.append(submenuGrolsh)
        self.menubeer.append(submenuHeineken)
        self.menubeer.append(submenuUttinger)
        self.menubeer.append(submenu30L_Uttinger)
        self.menubeer.append(gtk.SeparatorMenuItem())
        self.menubeer.append(self.setcustomweight)
        
        self.menuoptions.append(suboptionsLed)
        self.menuoptions.append(suboptionsNixie)

        menuItemQuit.connect('activate', self.quit, "quit")

        submenuKeg.connect("toggled", self.on_button_toggled, "Keg", 15)
        submenuGrolsh.connect("toggled", self.on_button_toggled, "Grolsh", 14.3)
        submenuHeineken.connect("toggled", self.on_button_toggled, "Heineken", 17)
        submenuUttinger.connect("toggled", self.on_button_toggled, "Uttinger", 19)
        submenu30L_Uttinger.connect("toggled", self.on_button_toggled, "Uttinger30L", 12)
        self.setcustomweight.connect("toggled", self.on_button_toggled, "VulGewichtIn", 2)

        ## Show all in menu (instead of calling .show() for each item)
        self.menu.show_all()

        ## Add constructed menu as indicator menu
        self.ind.set_menu(self.menu)    
    def main(self):
        ## gtk.timeout_add(PING_FREQUENCY, self.updatebeer)
        gtk.main()
        return 0

if __name__ == "__main__":
   bier = '{nrbier}L'.format(nrbier = 10.0)
   indicator = MyIndicator()
   indicator.ind.set_label(bier)
   #indicator.ind.set_use_markup(True)
   indicator.main()
