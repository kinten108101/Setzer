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
from gi.repository import Gtk, Adw


class PageEditor(object):

    def __init__(self, preferences, settings):
        self.view = PageEditorView()
        self.preferences = preferences
        self.settings = settings

    def init(self):
        self.view.row_space_tab.set_selected(
            self.get_enum_idx_from_dict_space_tab()
        )

        self.view.row_space_tab.connect(
            "notify::selected",
            self.update_enum_from_dict_space_tab,
        )

        self.view.tab_width_spinbutton.set_value(self.settings.get_value('preferences', 'tab_width'))
        self.view.tab_width_spinbutton.connect('value-changed', self.preferences.spin_button_changed, 'tab_width')

        self.view.option_show_line_numbers.set_active(self.settings.get_value('preferences', 'show_line_numbers'))
        self.view.option_show_line_numbers.connect('notify::active', self.on_active_prop_changed, 'show_line_numbers')

        self.view.option_line_wrapping.set_active(self.settings.get_value('preferences', 'enable_line_wrapping'))
        self.view.option_line_wrapping.connect('notify::active', self.on_active_prop_changed, 'enable_line_wrapping')

        self.view.option_code_folding.set_active(self.settings.get_value('preferences', 'enable_code_folding'))
        self.view.option_code_folding.connect('notify::active', self.on_active_prop_changed, 'enable_code_folding')

        self.view.option_highlight_current_line.set_active(self.settings.get_value('preferences', 'highlight_current_line'))
        self.view.option_highlight_current_line.connect('notify::active', self.on_active_prop_changed, 'highlight_current_line')

        self.view.option_highlight_matching_brackets.set_active(self.settings.get_value('preferences', 'highlight_matching_brackets'))
        self.view.option_highlight_matching_brackets.connect('notify::active', self.on_active_prop_changed, 'highlight_matching_brackets')

    def on_active_prop_changed(self, object, pspec, preference_name):
        self.settings.set_value(
            "preferences",
            preference_name,
            object.get_active(),
        )

    def get_enum_idx_from_dict_space_tab(self):
        val = self.settings.get_value(
          "preferences",
          "spaces_instead_of_tabs",
        )
        if val is True:
            val = "space"
        else:
            val = "tab"
        options = list(self.view.dict_option_space_tab.keys())
        idx = -1
        try:
            idx = options.index(val)
        except ValueError:
            idx = 0
        return idx

    def update_enum_from_dict_space_tab(self, object, selected):
        options = list(self.view.dict_option_space_tab.keys())
        idx = self.view.row_space_tab.get_selected()
        val = None
        try:
            val = options[idx]
        except IndexError:
            print("error")
            val = 0
        if val == "space":
            val = True
        else:
            val = False
        self.settings.set_value("preferences", "spaces_instead_of_tabs", val)


class PageEditorView(Adw.PreferencesPage):

    def __init__(self):
        Adw.PreferencesPage.__init__(self)
        self.set_icon_name("text3-symbolic")

        self.dict_option_space_tab = dict()
        self.dict_option_space_tab["tab"] = [_("Tab")]
        self.dict_option_space_tab["space"] = [_("Space")]

        combo_model_space_tab = Gtk.StringList()

        for id in self.dict_option_space_tab:
            name = self.dict_option_space_tab[id][0]
            combo_model_space_tab.append(name)

        self.row_space_tab = Adw.ComboRow()
        self.row_space_tab.set_title(_("Tab _Mode"))
        self.row_space_tab.set_use_underline(True)
        self.row_space_tab.set_subtitle(_("What character should be used for each inserted tab stop"))
        self.row_space_tab.set_model(combo_model_space_tab)

        self.tab_width_spinbutton = Gtk.SpinButton.new_with_range(1, 8, 1)
        self.tab_width_spinbutton.set_can_focus(False)
        self.tab_width_spinbutton.set_valign(Gtk.Align.CENTER)

        self.row_tab_width = Adw.ActionRow()
        self.row_tab_width.set_title(_("Tab _Width"))
        self.row_tab_width.set_use_underline(True)
        self.row_tab_width.set_subtitle(_("Adjust the amount of spaces per width"))
        self.row_tab_width.add_suffix(self.tab_width_spinbutton)
        self.row_tab_width.set_activatable_widget(self.tab_width_spinbutton)

        tab_stop_group = Adw.PreferencesGroup()
        tab_stop_group.set_title(_("Tab Stops"))
        tab_stop_group.add(self.row_space_tab)
        tab_stop_group.add(self.row_tab_width)

        self.option_show_line_numbers = Gtk.Switch()
        self.option_show_line_numbers.set_can_focus(False)
        self.option_show_line_numbers.set_valign(Gtk.Align.CENTER)

        self.row_show_line_numbers = Adw.ActionRow()
        self.row_show_line_numbers.set_title(_("Show _Line Numbers"))
        self.row_show_line_numbers.set_use_underline(True)
        self.row_show_line_numbers.set_subtitle(_("Display line numbers next to each line of code"))
        self.row_show_line_numbers.add_suffix(self.option_show_line_numbers)
        self.row_show_line_numbers.set_activatable_widget(self.option_show_line_numbers)

        line_numbers_group = Adw.PreferencesGroup()
        line_numbers_group.set_title(_("Line Numbers"))
        line_numbers_group.add(self.row_show_line_numbers)

        self.option_line_wrapping = Gtk.Switch()
        self.option_line_wrapping.set_can_focus(False)
        self.option_line_wrapping.set_valign(Gtk.Align.CENTER)

        self.row_line_wrapping = Adw.ActionRow()
        self.row_line_wrapping.set_title(_("_Wrap Text"))
        self.row_line_wrapping.set_use_underline(True)
        self.row_line_wrapping.set_subtitle(_("Should text be wrapped when wider than the frame"))
        self.row_line_wrapping.add_suffix(self.option_line_wrapping)
        self.row_line_wrapping.set_activatable_widget(self.option_line_wrapping)

        line_wrapping_group = Adw.PreferencesGroup()
        line_wrapping_group.set_title(_("Wrapping"))
        line_wrapping_group.add(self.row_line_wrapping)

        self.option_code_folding = Gtk.Switch()
        self.option_code_folding.set_can_focus(False)
        self.option_code_folding.set_valign(Gtk.Align.CENTER)

        self.row_code_folding = Adw.ActionRow()
        self.row_code_folding.set_title(_("Enable Code _Folding"))
        self.row_code_folding.set_use_underline(True)
        self.row_code_folding.set_subtitle(_("Selectively hide or display parts of the code"))
        self.row_code_folding.add_suffix(self.option_code_folding)
        self.row_code_folding.set_activatable_widget(self.option_code_folding)

        code_folding_group = Adw.PreferencesGroup()
        code_folding_group.set_title(_("Code Folding"))
        code_folding_group.add(self.row_code_folding)

        self.option_highlight_current_line = Gtk.Switch()
        self.option_highlight_current_line.set_can_focus(False)
        self.option_highlight_current_line.set_valign(Gtk.Align.CENTER)

        self.row_highlight_current_line = Adw.ActionRow()
        self.row_highlight_current_line.set_title(_("_Highlight Current Line"))
        self.row_highlight_current_line.set_use_underline(True)
        self.row_highlight_current_line.set_subtitle(_("Make the current line stand out with highlights"))
        self.row_highlight_current_line.add_suffix(self.option_highlight_current_line)
        self.row_highlight_current_line.set_activatable_widget(self.option_highlight_current_line)

        self.option_highlight_matching_brackets = Gtk.Switch()
        self.option_highlight_matching_brackets.set_can_focus(False)
        self.option_highlight_matching_brackets.set_valign(Gtk.Align.CENTER)

        self.row_highlight_matching_brackets = Adw.ActionRow()
        self.row_highlight_matching_brackets.set_title(_("Highlight Matching Brac_kets"))
        self.row_highlight_matching_brackets.set_use_underline(True)
        self.row_highlight_matching_brackets.set_subtitle(_("Use cursor position to highlight matching brackets, braces, parenthesis, and more"))
        self.row_highlight_matching_brackets.add_suffix(self.option_highlight_matching_brackets)
        self.row_highlight_matching_brackets.set_activatable_widget(self.option_highlight_matching_brackets)

        highlight_group = Adw.PreferencesGroup()
        highlight_group.set_title(_("Highlighting"))
        highlight_group.add(self.row_highlight_current_line)
        highlight_group.add(self.row_highlight_matching_brackets)

        self.add(tab_stop_group)
        self.add(line_numbers_group)
        self.add(line_wrapping_group)
        self.add(code_folding_group)
        self.add(highlight_group)

