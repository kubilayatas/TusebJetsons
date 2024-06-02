# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 17:24:22 2024

@author: kubil
"""

import gi

gi.require_version("Gtk","3.0")
from gi.repository import Gtk as gtk


class Main:
    def __init__(self):
        gladeFile = "./Deneme1.glade"
        self.builder = gtk.Builder()
        self.builder.add_from_file(gladeFile)
        self.builder.connect_signals(self)
        
        window = self.builder.get_object("MainWindow")
        window.connect("delete-event", gtk.main_quit)
        window.show()




if __name__ == "__main__":
    main = Main()
    gtk.main()