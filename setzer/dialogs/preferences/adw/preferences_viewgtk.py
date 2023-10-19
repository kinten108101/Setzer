import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw


class NoteBook(object):

    def __init__(self, preferences_window):
        self.preferences_window = preferences_window

    def append_page(self, page, label_obj):
        page.set_title(label_obj.get_label())
        page.set_use_underline(True)
        try:
            self.preferences_window.add(page)
        except e:
            print(e)


PreferencesWindowXml = '''\
<interface>
    <template class="SetzerPreferencesAdwWindow" parent="AdwPreferencesWindow">
        <child>
            <object class="GtkShortcutController" id="shortcut_controller">
            </object>
        </child>
    </template>
</interface>
'''


@Gtk.Template(string=PreferencesWindowXml)
class PreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = "SetzerPreferencesAdwWindow"

    shortcut_controller = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope.LOCAL)

    def connect(self, signal, callback, *args):
        if (signal == 'response'):
            return super().connect("notify", self.default_callback)
        else:
            return super().connect(signal, callback, *args)

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
