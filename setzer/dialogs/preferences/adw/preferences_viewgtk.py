import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Adw


class NoteBook(object):

    def __init__(self, preferences_window):
        self.preferences_window = preferences_window

    def append_page(self, page, label_obj):
        page.set_title(label_obj.get_label())
        self.preferences_window.add(page)


class PreferencesWindow(Adw.PreferencesWindow):

    def connect(self, signal, *args):
        if (signal == 'response'):
            return super().connect("notify", self.default_callback)
        else:
            return super().connect(signal, args)

    def default_callback(*args):
        pass


class Preferences(object):

    def __init__(self, main_window):
        self.dialog = PreferencesWindow()
        self.dialog.set_destroy_with_parent(True)
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(main_window)
        self.notebook = NoteBook(self.dialog)

    def response(self, args):
        self.dialog.response(args)

    def __del__(self):
        self.dialog.destroy()
