import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

def CloseConfirmationView(documents, parent_window):
    view = Gtk.MessageDialog()
    view.set_transient_for(parent_window)
    view.set_modal(True)
    view.set_property('message-type', Gtk.MessageType.QUESTION)

    chooser = None

    if len(documents) == 1:
        view.set_property('text', _('Document »{document}« has unsaved changes.').format(document=documents[0].get_displayname()))
        view.set_property('secondary-text', _('If you close without saving, these changes will be lost.'))

    if len(documents) >= 2:
        view.set_property('text', _('There are {amount} documents with unsaved changes.\nSave changes before closing?').format(amount=str(len(documents))))
        view.set_property('secondary-text', _('Select the documents you want to save:'))
        view.get_message_area().get_first_child().set_xalign(0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(446, 112)
        scrolled_window.get_style_context().add_class('close-confirmation-list')
        chooser = Gtk.ListBox()
        chooser.set_selection_mode(Gtk.SelectionMode.NONE)
        chooser.set_can_focus(False)
        counter = 0
        for document in documents:
            button = Gtk.CheckButton.new_with_label(document.get_displayname())
            button.set_name('document_to_save_checkbutton_' + str(counter))
            button.set_active(True)
            button.set_can_focus(False)
            chooser.append(button)
            counter += 1
        scrolled_window.set_child(chooser)
            
        secondary_text_label = Gtk.Label.new(_('If you close without saving, all changes will be lost.'))
        message_area = view.get_message_area()
        message_area.append(scrolled_window)
        message_area.append(secondary_text_label)

    view.add_buttons(_('Close _without Saving'), Gtk.ResponseType.NO, _('_Cancel'), Gtk.ResponseType.CANCEL, _('_Save'), Gtk.ResponseType.YES)
    view.set_default_response(Gtk.ResponseType.YES)
    return [view, chooser]