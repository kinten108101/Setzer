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


class HeaderbarController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

        actions = self.model.workspace.actions.actions
        self.view.button_latex.set_detailed_action('win.new-latex-document')
        self.view.button_bibtex.set_detailed_action('win.new-bibtex-document')
        self.view.button_save_session.set_detailed_action('win.save-session')
        self.view.button_save_as.set_detailed_action('win.save-as')
        self.view.button_save_all.set_detailed_action('win.save-all')
        self.view.button_preferences.set_detailed_action('win.show-preferences-dialog')
        self.view.button_shortcuts.set_detailed_action('win.show-shortcuts-dialog')
        self.view.button_about.set_detailed_action('win.show-about-dialog')
        self.view.button_close_all.set_detailed_action('win.close-all-documents')
        self.view.button_close_active.set_detailed_action('win.close-active-document')
        self.view.button_quit.set_detailed_action('win.quit')

    def on_new_document_button_click(self, button, action):
        self.view.new_document_popover.popdown()
        action.activate()

    def on_hamburger_button_click(self, button, action):
        self.view.hamburger_popover.popdown()
        action.activate()


