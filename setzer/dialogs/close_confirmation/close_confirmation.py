#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

import os.path
from setzer.dialogs.close_confirmation.close_confirmation_adw_viewgtk import CloseConfirmationView


class CloseConfirmationDialog(object):
    ''' This dialog is asking users to save unsaved documents or discard their changes. '''

    def __init__(self, main_window, workspace, save_document_dialog):
        self.main_window = main_window
        self.workspace = workspace
        self.parameters = None
        self.save_document_dialog = save_document_dialog

    def run(self, parameters, callback):
        if parameters['unsaved_documents'] == None: return

        self.parameters = parameters
        self.callback = callback

        self.setup(self.parameters['unsaved_documents'])

        self.view.show()
        self.signal_connection_id = self.view.connect('response', self.process_response)

    def process_response(self, view, response_id):
        documents_not_save_to_close = list()
        return_to_active_document = False
        documents = self.parameters['unsaved_documents']

        if response_id == Gtk.ResponseType.NO:
            self.workspace.save_to_disk()
            all_save_to_close = True
        elif response_id == Gtk.ResponseType.YES:
            selected_documents = list()
            if len(documents) == 1:
                selected_documents.append(documents[0])
            else:
                for child in self.chooser.get_children():
                    if child.get_child().get_active():
                        number = int(child.get_child().get_name()[29:])
                        selected_documents.append(documents[number])
            for document in selected_documents:
                if document.get_filename() == None:
                    self.workspace.set_active_document(document)
                    return_to_active_document = True

                    if not self.save_document_dialog.run(document):
                        documents_not_save_to_close.append(document)
                else:
                    document.save_to_disk()
            if return_to_active_document == True:
                self.workspace.set_active_document(document)

            self.workspace.save_to_disk()
            if len(documents_not_save_to_close) >= 1:
                self.workspace.set_active_document(documents_not_save_to_close[-1])
                all_save_to_close = False
            else:
                all_save_to_close = True
        else:
            all_save_to_close = False
            documents_not_save_to_close = documents

        self.close()
        response = {'all_save_to_close': all_save_to_close, 'not_save_to_close_documents': documents_not_save_to_close}
        self.callback(self.parameters, response)

    def close(self):
        self.view.hide()
        self.view.disconnect(self.signal_connection_id)
        del(self.view)

    def setup(self, documents):
        self.view, self.chooser = CloseConfirmationView(documents, self.main_window)
