import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
import os.path

from setzer.dialogs.close_confirmation.adw.document_to_save import DocumentToSaveView
from setzer.dialogs.close_confirmation.adw.document_to_save import DocumentToSaveRow
from setzer.dialogs.close_confirmation.adw.message_dialog import AdaptedAdwMessageDialog as MessageDialog


def CloseConfirmationView(documents, parent_window):
    view = MessageDialog()
    view.dialog.get_style_context().add_class('close-confirmation-dialog')
    view.set_transient_for(parent_window)
    view.set_modal(True)
    view.set_property('message-type', Gtk.MessageType.QUESTION)

    view.set_property('text', _('Save Changes?'))
    # FIXME(kinten): body_label will have incorrect bounding box depending on text content and extra_child
    # Here we reused text from GNOME Text Editor which has been shown to work correctly
    view.set_property('secondary-text', _('Open documents contain unsaved changes. Changes which are not saved will be permanently lost.'))

    chooser = None

    if len(documents) >= 1:
        view.get_message_area().get_first_child().set_xalign(0)

        documents_view = DocumentToSaveView()
        chooser = documents_view.chooser
        counter = 0
        for document in documents:
            title = document.get_basename()
            filename = document.get_filename()
            if filename is None:
                button = DocumentToSaveRow(title)
            else:
                directory = os.path.split(filename.replace(os.path.expanduser('~'), '~'))[0]
                button = DocumentToSaveRow(title, directory)
            button.set_name('document_to_save_checkbutton_' + str(counter))
            button.set_active(True)
            button.set_can_focus(False)
            chooser.append(button)
            counter += 1
        message_area = view.get_message_area()
        message_area.append(documents_view)

    view.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL, _('_Discard All'), Gtk.ResponseType.NO, _('_Save'), Gtk.ResponseType.YES)
    view.set_default_response(Gtk.ResponseType.YES)
    return [view, chooser]
