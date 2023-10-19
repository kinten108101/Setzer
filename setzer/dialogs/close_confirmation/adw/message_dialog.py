import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw


class AdaptedAdwMessageDialog(object):

    last_id = 0

    def generate_id():
        AdaptedAdwMessageDialog.last_id += 1
        return AdaptedAdwMessageDialog.last_id

    def __init__(self):
        super().__init__()
        self.response_map = dict()
        self.dialog = Adw.MessageDialog()
        self.message_area = Gtk.Box()

        # NOTE(kinten): this message area is expected to contain the body label as child object, but adwmessagedialog doesnt allow that.
        # so we have a non-useable label here so that the code can at least run
        self.placeholder_label = Gtk.Label()
        self.placeholder_label.set_visible(False)
        self.message_area.append(self.placeholder_label)

        self.message_area.set_orientation(Gtk.Orientation.VERTICAL)
        self.dialog.set_extra_child(self.message_area)

    def set_transient_for(self, window):
        self.dialog.set_transient_for(window)

    def set_modal(self, val):
        self.dialog.set_modal(val)

    def set_property(self, name, value):
        if name == 'text':
            self.dialog.set_heading(value)
        elif name == 'secondary-text':
            self.dialog.set_body(value)

    def add_buttons(self, *args):
        assert len(args) % 2 == 0
        i = 0
        for k in range(0, int(len(args) / 2)):
            label = args[i]
            gtkresponse = args[i + 1]
            id = str(AdaptedAdwMessageDialog.generate_id())
            self.response_map[id] = gtkresponse
            self.dialog.add_response(id, label)
            if gtkresponse == Gtk.ResponseType.YES:
                self.dialog.set_response_appearance(id, Adw.ResponseAppearance.SUGGESTED)
            elif gtkresponse == Gtk.ResponseType.NO:
                self.dialog.set_response_appearance(id, Adw.ResponseAppearance.DESTRUCTIVE)
            i += 2

    def set_default_response(self, id):
        self.dialog.set_default_response(str(id))

    def get_message_area(self):
        return self.message_area

    def show(self):
        self.dialog.show()

    def hide(self):
        self.dialog.hide()

    def connect(self, signal, callback):
        if signal == 'response':
            def on_adw_message_dialog_responded(object, response):
                if response == 'close':
                    callback(self, Gtk.ResponseType.CANCEL)
                else:
                    gtkresponse = self.response_map[response]
                    callback(self, gtkresponse)
            return self.dialog.connect(signal, on_adw_message_dialog_responded)
        else:
            return self.dialog.connect(signal, callback)

    def disconnect(self, handler):
        self.dialog.disconnect(handler)
