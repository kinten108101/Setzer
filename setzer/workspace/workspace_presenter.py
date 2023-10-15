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
from gi.repository import Adw
from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager

import os.path


class WorkspacePresenter(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.settings = ServiceLocator.get_settings()

        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('new_inactive_document', self.on_new_inactive_document)
        self.workspace.connect('set_show_symbols_or_document_structure', self.on_set_show_symbols_or_document_structure)
        self.workspace.connect('set_show_preview_or_help', self.on_set_show_preview_or_help)
        self.workspace.connect('show_build_log_state_change', self.on_show_build_log_state_change)
        self.settings.connect('settings_changed', self.on_settings_changed)

        self.activate_welcome_screen_mode()
        self.update_font()
        self.update_colors()
        self.setup_paneds()
        self.setup_colors()

    def on_settings_changed(self, settings, parameter):
        section, item, value = parameter

        if item in ['font_string', 'use_system_font']:
            self.update_font()

        if item in ['color_scheme', 'follow_mode']:
            self.update_colors()

    def on_new_document(self, workspace, document):
        if document.is_latex_document():
            self.main_window.latex_notebook.append_page(document.view)
        elif document.is_bibtex_document():
            self.main_window.bibtex_notebook.append_page(document.view)
        else:
            self.main_window.others_notebook.append_page(document.view)

    def on_document_removed(self, workspace, document):
        if document.is_latex_document():
            notebook = self.main_window.latex_notebook
        elif document.is_bibtex_document():
            notebook = self.main_window.bibtex_notebook
        else:
            notebook = self.main_window.others_notebook
        
        notebook.remove_page(notebook.page_num(document.view))

        if self.workspace.active_document == None:
            self.activate_welcome_screen_mode()

    def on_new_active_document(self, workspace, document):
        if document.is_latex_document():
            notebook = self.main_window.latex_notebook
            notebook.set_current_page(notebook.page_num(document.view))
            document.view.source_view.grab_focus()
            try: self.main_window.preview_paned_overlay.add_overlay(document.autocomplete.widget.view)
            except AttributeError: pass
            self.activate_latex_documents_mode()
        elif document.is_bibtex_document():
            notebook = self.main_window.bibtex_notebook
            notebook.set_current_page(notebook.page_num(document.view))
            document.view.source_view.grab_focus()
            self.activate_bibtex_documents_mode()
        else:
            notebook = self.main_window.others_notebook
            notebook.set_current_page(notebook.page_num(document.view))
            document.view.source_view.grab_focus()
            self.activate_other_documents_mode()

    def on_new_inactive_document(self, workspace, document):
        if document.is_latex_document():
            try: self.main_window.preview_paned_overlay.remove_overlay(document.autocomplete.widget.view)
            except AttributeError: pass

    def on_set_show_symbols_or_document_structure(self, workspace):
        if self.workspace.show_symbols:
            self.main_window.sidebar.set_visible_child_name('symbols')
        elif self.workspace.show_document_structure:
            self.main_window.sidebar.set_visible_child_name('document_structure')
        self.focus_active_document()
        self.main_window.sidebar_paned.set_show_widget(self.workspace.show_symbols or self.workspace.show_document_structure)
        self.main_window.sidebar_paned.animate(True)

    def on_set_show_preview_or_help(self, workspace):
        if self.workspace.show_preview:
            self.main_window.preview_help_stack.set_visible_child_name('preview')
            self.focus_active_document()
        elif self.workspace.show_help:
            self.main_window.preview_help_stack.set_visible_child_name('help')
            if self.main_window.help_panel.stack.get_visible_child_name() == 'search':
                self.main_window.help_panel.search_entry.set_text('')
                self.main_window.help_panel.search_entry.grab_focus()
            else:
                self.focus_active_document()
        else:
            self.focus_active_document()
        self.main_window.preview_paned.set_show_widget(self.workspace.show_preview or self.workspace.show_help)
        self.main_window.preview_paned.animate(True)

    def on_show_build_log_state_change(self, workspace, show_build_log):
        self.main_window.build_log_paned.set_show_widget(self.workspace.show_build_log)
        self.main_window.build_log_paned.animate(True)

    def activate_welcome_screen_mode(self):
        self.main_window.mode_stack.set_visible_child_name('welcome_screen')

    def activate_latex_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('latex_documents')

    def activate_bibtex_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('bibtex_documents')

    def activate_other_documents_mode(self):
        self.main_window.mode_stack.set_visible_child_name('other_documents')

    def focus_active_document(self):
        active_document = self.workspace.get_active_document()
        if active_document != None:
            active_document.view.source_view.grab_focus()

    def update_font(self):
        if self.settings.get_value('preferences', 'use_system_font'):
            FontManager.font_string = FontManager.default_font_string
        else:
            FontManager.font_string = self.settings.get_value('preferences', 'font_string')
        FontManager.propagate_font_setting()

    def update_colors(self):
        name = self.settings.get_value('preferences', 'color_scheme')
        follow_mode = self.settings.get_value('preferences', 'follow_mode')
        style_manager = Adw.StyleManager.get_default()
        adw_color_scheme = 0
        if follow_mode == 'manual':
            if "dark" in name:
                adw_color_scheme = 4
            else:
                adw_color_scheme = 1
        style_manager.set_color_scheme(adw_color_scheme)

    def setup_paneds(self):
        show_sidebar = (self.workspace.show_symbols or self.workspace.show_document_structure)
        show_preview_help = (self.workspace.show_preview or self.workspace.show_help)
        show_build_log = self.workspace.get_show_build_log()

        sidebar_position = self.workspace.settings.get_value('window_state', 'sidebar_paned_position')
        preview_position = self.workspace.settings.get_value('window_state', 'preview_paned_position')
        build_log_position = self.workspace.settings.get_value('window_state', 'build_log_paned_position')

        if sidebar_position in [None, -1]: self.main_window.sidebar_paned.set_start_on_first_show()
        if preview_position in [None, -1]: self.main_window.preview_paned.set_center_on_first_show()
        if build_log_position in [None, -1]: self.main_window.build_log_paned.set_end_on_first_show()

        if self.workspace.show_symbols: self.main_window.sidebar.set_visible_child_name('symbols')
        elif self.workspace.show_document_structure: self.main_window.sidebar.set_visible_child_name('document_structure')

        if self.workspace.show_preview: self.main_window.preview_help_stack.set_visible_child_name('preview')
        elif self.workspace.show_help: self.main_window.preview_help_stack.set_visible_child_name('help')

        self.main_window.sidebar_paned.first_set_show_widget(show_sidebar)
        self.main_window.preview_paned.first_set_show_widget(show_preview_help)
        self.main_window.build_log_paned.first_set_show_widget(show_build_log)

        self.main_window.sidebar_paned.set_target_position(sidebar_position)
        self.main_window.preview_paned.set_target_position(preview_position)
        self.main_window.build_log_paned.set_target_position(build_log_position)

        self.main_window.headerbar.symbols_toggle.set_active(self.workspace.show_symbols)
        self.main_window.headerbar.document_structure_toggle.set_active(self.workspace.show_document_structure)
        self.main_window.headerbar.preview_toggle.set_active(self.workspace.show_preview)
        self.main_window.headerbar.help_toggle.set_active(self.workspace.show_help)

    def setup_colors(self):
        style_manager = Adw.StyleManager.get_default()
        self.on_adw_style_manager_notify_dark(style_manager)
        style_manager.connect('notify::dark', self.on_adw_style_manager_notify_dark)

    def on_adw_style_manager_notify_dark(self, object, pspec=None):
        name = 'default'
        if object.get_dark():
            name = 'default-dark'
        print(name)
        path = os.path.join(ServiceLocator.get_resources_path(), 'themes', name + '.css')
        self.main_window.css_provider_colors.load_from_path(path)
        try: self.workspace.help_panel.update_colors()
        except AttributeError: pass