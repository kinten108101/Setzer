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
from gi.repository import GLib
from gi.repository import Gio

import setzer.workspace.document_switcher.document_switcher_viewgtk as document_switcher_viewgtk
import setzer.workspace.document_chooser.document_chooser_viewgtk as document_chooser_viewgtk
from setzer.helpers.popover_menu_builder import MenuBuilderTest


class HeaderBar(Gtk.HeaderBar):
    ''' Title bar of the app, contains global controls '''

    def __init__(self):
        Gtk.HeaderBar.__init__(self)

        # sidebar toggles
        self.document_structure_toggle = Gtk.ToggleButton()
        self.document_structure_toggle.set_child(Gtk.Image.new_from_icon_name('document-structure-symbolic'))
        self.document_structure_toggle.set_can_focus(False)
        self.document_structure_toggle.set_tooltip_text(_('Toggle document structure') + ' (F2)')

        self.symbols_toggle = Gtk.ToggleButton()
        self.symbols_toggle.set_child(Gtk.Image.new_from_icon_name('own-symbols-misc-text-symbolic'))
        self.symbols_toggle.set_can_focus(False)
        self.symbols_toggle.set_tooltip_text(_('Toggle symbols') + ' (F3)')

        self.sidebar_toggles_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.sidebar_toggles_box.append(self.document_structure_toggle)
        self.sidebar_toggles_box.append(self.symbols_toggle)
        self.sidebar_toggles_box.get_style_context().add_class('linked')

        self.pack_start(self.sidebar_toggles_box)

        # open document buttons
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + _('Ctrl') + '+O)')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')

        self.document_chooser = document_chooser_viewgtk.DocumentChooser()
        self.open_document_button_label = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        self.open_document_button_label.append(Gtk.Label.new(_('Open')))
        self.open_document_button_label.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))
        self.open_document_button = Gtk.MenuButton()
        self.open_document_button.get_style_context().add_class('flat')
        self.open_document_button.set_tooltip_text(_('Open a document') + ' (' + _('Shift') + '+' + _('Ctrl') + '+O)')
        self.open_document_button.set_child(self.open_document_button_label)
        self.open_document_button.set_popover(self.document_chooser)

        # new document buttons
        self.button_latex = MenuBuilderTest.create_button(_('New LaTeX Document'), shortcut=_('Ctrl') + '+N')
        self.button_bibtex = MenuBuilderTest.create_button(_('New BibTeX Document'))

        self.new_document_popover = MenuBuilderTest.create_menu()

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        box.append(Gtk.Image.new_from_icon_name('document-new-symbolic'))
        box.append(Gtk.Image.new_from_icon_name('pan-down-symbolic'))

        self.new_document_button = Gtk.MenuButton()
        self.new_document_button.set_child(box)
        self.new_document_button.set_can_focus(False)
        self.new_document_button.set_tooltip_text(_('Create a new document'))
        self.new_document_button.get_style_context().add_class('new-document-menu-button')
        self.new_document_button.get_style_context().add_class('flat')
        self.new_document_button.set_popover(self.new_document_popover)

        self.pack_start(self.open_document_button)
        self.pack_start(self.open_document_blank_button)
        self.pack_start(self.new_document_button)

        # workspace menu
        self.session_file_buttons = list()
        self.insert_workspace_menu()

        # save document button
        self.save_document_button = Gtk.Button.new_with_label(_('Save'))
        self.save_document_button.set_can_focus(False)
        self.save_document_button.set_tooltip_text(_('Save the current document') + ' (' + _('Ctrl') + '+S)')
        self.save_document_button.set_action_name('win.save')
        self.save_document_button.set_visible(False)
        self.pack_end(self.save_document_button)

        # help and preview toggles
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.preview_toggle = Gtk.ToggleButton()
        self.preview_toggle.set_child(Gtk.Image.new_from_icon_name('view-paged-symbolic'))
        self.preview_toggle.set_can_focus(False)
        self.preview_toggle.set_tooltip_text(_('Toggle preview') + ' (F9)')
        box.append(self.preview_toggle)
        self.help_toggle = Gtk.ToggleButton()
        self.help_toggle.set_child(Gtk.Image.new_from_icon_name('help-browser-symbolic'))
        self.help_toggle.set_can_focus(False)
        self.help_toggle.set_tooltip_text(_('Toggle help') + ' (F1)')
        box.append(self.help_toggle)
        box.get_style_context().add_class('linked')
        self.pack_end(box)

        # build button wrapper
        self.build_wrapper = Gtk.CenterBox()
        self.build_wrapper.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.pack_end(self.build_wrapper)

        # title / open documents popover
        self.center_widget = document_switcher_viewgtk.OpenDocsButton()
        self.set_title_widget(self.center_widget)

    def insert_workspace_menu(self):
        self.hamburger_popover = MenuBuilderTest.create_menu()

        self.button_save_as = MenuBuilderTest.create_button(_('Save Document As') + '...', shortcut=_('Shift') + '+' + _('Ctrl') + '+S')
        self.button_save_all = MenuBuilderTest.create_button(_('Save All Documents'))
        self.button_session = MenuBuilderTest.create_menu_button(_('Session'))

        self.button_preferences = MenuBuilderTest.create_button(_('Preferences'))
        self.button_shortcuts = MenuBuilderTest.create_button(_('Keyboard Shortcuts'), shortcut=_('Ctrl') + '+?')
        self.button_about = MenuBuilderTest.create_button(_('About'))
        self.button_close_all = MenuBuilderTest.create_button(_('Close All Documents'))
        self.button_close_active = MenuBuilderTest.create_button(_('Close Document'), shortcut=_('Ctrl') + '+W')
        self.button_quit = MenuBuilderTest.create_button(_('Quit'), shortcut=_('Ctrl') + '+Q')

        box_session = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.menu_button = Gtk.MenuButton()
        image = Gtk.Image.new_from_icon_name('open-menu-symbolic')
        self.menu_button.get_style_context().add_class('flat')
        self.menu_button.set_child(image)
        self.menu_button.set_can_focus(False)
        self.menu_button.set_popover(self.hamburger_popover)
        self.pack_end(self.menu_button)

        self.session_explaination = Gtk.Label.new(_('Save the list of open documents in a session file\nand restore it later, a convenient way to work\non multiple projects.'))
        self.session_explaination.set_xalign(0)
        self.session_explaination.get_style_context().add_class('explaination')
        self.session_explaination.set_margin_top(8)
        self.session_explaination.set_margin_bottom(11)

        # session submenu
        MenuBuilderTest.add_page(self.hamburger_popover, 'session', _('Session'))
        MenuBuilderTest.link_to_menu(self.hamburger_popover, self.button_session, 'session')

        self.button_restore_session = MenuBuilderTest.create_button(_('Restore Previous Session') + '...')
        self.button_save_session = MenuBuilderTest.create_button(_('Save Current Session') + '...')

        self.session_box_separator = Gtk.Separator()
        self.session_box_separator.hide()

        self.prev_sessions_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

    def update_actions(self):
        MenuBuilderTest.add_item(self.new_document_popover, self.button_latex)
        MenuBuilderTest.add_item(self.new_document_popover, self.button_bibtex)

        MenuBuilderTest.add_item(self.hamburger_popover, self.button_save_as)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_save_all)
        MenuBuilderTest.add_separator(self.hamburger_popover)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_session)
        MenuBuilderTest.add_separator(self.hamburger_popover)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_preferences)
        MenuBuilderTest.add_separator(self.hamburger_popover)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_shortcuts)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_about)
        MenuBuilderTest.add_separator(self.hamburger_popover)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_close_all)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_close_active)
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_quit)

        MenuBuilderTest.add_custom_widget(self.hamburger_popover, self.session_explaination, pagename='session')
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_restore_session, pagename='session')
        MenuBuilderTest.add_item(self.hamburger_popover, self.button_save_session, pagename='session')
        MenuBuilderTest.add_custom_widget(self.hamburger_popover, self.session_box_separator, pagename='session')
        MenuBuilderTest.add_custom_widget(self.hamburger_popover, self.prev_sessions_box, pagename='session')
