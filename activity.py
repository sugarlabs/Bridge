
import sys
sys.path.insert(0, "lib")
import gtk
import pygame

from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import ActivityToolbarButton
from sugar.graphics.toolbutton import ToolButton
from sugar.activity.widgets import StopButton
from gettext import gettext as _

import sugargame.canvas

import tools
import physics


class BridgeActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.game = physics.PhysicsGame()
        self.build_toolbar()
        self._pygamecanvas = sugargame.canvas.PygameCanvas(self)
        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.grab_focus()
        self._pygamecanvas.run_pygame(self.game.run)

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        self.blocklist = [] 
        self.radioList = {}
        for c in tools.allTools:                             
            button = ToolButton(c.icon)
            button.set_tooltip(_(c.toolTip))
            button.connect('clicked',self.radioClicked)
            toolbar_box.toolbar.insert(button, -1)    
            button.show()
            self.radioList[button] = c.name
       
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.show_all()

    def radioClicked(self,button):
        evt = pygame.event.Event(pygame.USEREVENT, action=self.radioList[button])
        pygame.event.post(evt)

    def read_file(self, file_path):
        pass

    def write_file(self, file_path):
        pass

