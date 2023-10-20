import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw, Pango


class DocumentToSaveRow(Adw.ActionRow):

    def __init__(self, title, subtitle=None):
        super().__init__()
        self.set_title(title)
        if subtitle is not None:
            self.set_subtitle(subtitle)
        self.checkbutton = Gtk.CheckButton()
        self.add_prefix(self.checkbutton)
        self.set_activatable_widget(self.checkbutton)

    def get_child(self):
        # FIXME(kinten): For some reasons, when a listbox is in an adwpreferencesgroup, calling list.get_row will
        # return child widget instead of the listboxrow wrapper. This method here is to deal with that scenario
        return self

    def set_active(self, value):
        self.checkbutton.set_active(value)

    def get_active(self):
        return self.checkbutton.get_active()


class DocumentToSaveView(Adw.PreferencesPage):

    def __init__(self):
        super().__init__()

        self.chooser = Gtk.ListBox()
        self.chooser.set_selection_mode(Gtk.SelectionMode.NONE)
        self.chooser.get_style_context().add_class('boxed-list')

        group = Adw.PreferencesGroup()
        group.add(self.chooser)
        self.add(group)