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
gi.require_version('GtkSource', '5')
import os, os.path
import shutil
import xml.etree.ElementTree as ET
from gi.repository import GObject, Gtk, Adw, GLib, Pango, GtkSource
from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager

class FontChooserButton(Gtk.Button):

    font_set = GObject.Signal()

    def __init__(self, parent_window):
        Gtk.Button.__init__(self)
        self.__doc__ = '''
Custom FontChooserButton that has Gtk.Button styles, hence has the .flat style.
        '''
        self.label_widget = Gtk.Label()
        self.label_widget.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.label_widget.set_size_request(160, -1)
        self.set_child(self.label_widget)

        self.dialog = Gtk.FontChooserDialog()
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(None)
        self.dialog.set_hide_on_close(True)
        self.dialog.connect('response', self.on_font_dialog_response)
        self.connect('clicked', self.on_clicked)
        self.connect('font_set', self.on_font_set)

    def on_clicked(self, object):
        self.dialog.show()

    def on_font_set(self, object):
        self.label_widget.set_label(self.dialog.get_font())

    def on_font_dialog_response(self, font_dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.emit('font_set')
        self.dialog.close()

    def get_font(self):
        return self.dialog.get_font()

    def set_font(self, font_string):
        self.label_widget.set_label(font_string)
        self.dialog.set_font(font_string)

    def get_font_size(self):
        return self.dialog.get_font_size()

    def set_font_size(self, size):
        self.dialog.set_font_size(size)

    def get_font_desc(self):
        return self.dialog.get_font_desc()

    def set_font_desc(self, desc):
        self.dialog.set_font_desc(desc)

    def connect(self, signal, callback, *userdata):
        if signal in ['notify::font']:
            self.dialog.connect(signal, callback, *userdata)
        else:
            super().connect(signal, callback, *userdata)

    def disconnect(self, handler):
        self.dialog.disconnect(signal)
        super().disconnect(handler)

    def emit(self, signal, *args):
        if signal in ['notify::font']:
            self.dialog.emit(signal, *args)
        else:
            super().emit(signal, *args)


class PageFontColor(object):

    def __init__(self, preferences, settings, main_window):
        self.view = PageFontColorView(main_window)
        self.preferences = preferences
        self.settings = settings
        self.main_window = main_window

    def init(self):
        self.update_switchers()
        self.view.style_switcher.connect('child-activated', self.on_style_switcher_changed)

        self.view.row_follow_mode.set_selected(
            self.get_enum_idx_from_dict_follow_mode()
        )

        self.view.row_follow_mode.connect(
            "notify::selected",
            self.update_enum_from_dict_follow_mode,
        )

        source_language_manager = ServiceLocator.get_source_language_manager()
        source_language = source_language_manager.get_language('latex')
        self.view.source_buffer.set_language(source_language)

        self.font_string = self.settings.get_value('preferences', 'font_string')
        self.view.font_chooser_button.set_font(self.font_string)
        self.view.font_chooser_button.connect('font_set', self.on_font_set)
        self.view.option_use_custom_font.set_active(not self.settings.get_value('preferences', 'use_system_font'))
        self.view.option_use_custom_font.connect('notify::active', self.on_use_custom_font_toggled)

        style_manager = Adw.StyleManager.get_default()
        self.on_adw_style_manager_notify_dark(style_manager)
        style_manager.connect('notify::dark', self.on_adw_style_manager_notify_dark)

    def on_adw_style_manager_notify_dark(self, object, pspec=None):
        name = 'default'
        if object.get_dark():
            name = 'default-dark'
        self.view.source_buffer.set_style_scheme(ServiceLocator.get_source_style_scheme_manager().get_scheme(name))

    def on_use_custom_font_toggled(self, button, pspec):
        self.settings.set_value('preferences', 'use_system_font', not button.get_active())

    def on_font_set(self, button):
        if button.get_font_size() < 6 * Pango.SCALE:
            font_desc = button.get_font_desc()
            font_desc.set_size(6 * Pango.SCALE)
            button.set_font_desc(font_desc)
        elif button.get_font_size() > 24 * Pango.SCALE:
            font_desc = button.get_font_desc()
            font_desc.set_size(24 * Pango.SCALE)
            button.set_font_desc(font_desc)

        self.settings.set_value('preferences', 'font_string', button.get_font())

    def on_notify_font(self, button, pspec):
        if button.get_font_size() < 6 * Pango.SCALE:
            font_desc = button.get_font_desc()
            font_desc.set_size(6 * Pango.SCALE)
            button.set_font_desc(font_desc)
        elif button.get_font_size() > 24 * Pango.SCALE:
            font_desc = button.get_font_desc()
            font_desc.set_size(24 * Pango.SCALE)
            button.set_font_desc(font_desc)

        self.settings.set_value('preferences', 'font_string', button.get_font())

    def on_style_switcher_changed(self, switcher, child_widget):
        style_scheme_preview = child_widget.get_child()
        value = style_scheme_preview.get_scheme().get_name()
        if value is not None:
            self.settings.set_value('preferences', 'color_scheme', value)

    def get_scheme_id_from_file(self, pathname):
        tree = ET.parse(pathname)
        root = tree.getroot()
        return root.attrib['id']

    def update_switchers(self):
        names = ['default', 'default-dark']
        dirname = os.path.join(ServiceLocator.get_config_folder(), 'themes')
        if os.path.isdir(dirname):
            names += [self.get_scheme_id_from_file(os.path.join(dirname, file)) for file in os.listdir(dirname)]
        for name in names:
            self.view.style_switcher.add_style(name)

        active_id = self.settings.get_value('preferences', 'color_scheme')
        if active_id in names:
            self.view.style_switcher.select_style(active_id)
        else:
            self.view.style_switcher.select_style('default')

    def get_enum_idx_from_dict_follow_mode(self):
        val = self.settings.get_value(
          "preferences",
          "follow_mode",
        )
        options = list(self.view.dict_option_follow_mode.keys())
        idx = -1
        try:
            idx = options.index(val)
        except ValueError:
            idx = 0
        return idx

    def update_enum_from_dict_follow_mode(self, object, selected):
        options = list(self.view.dict_option_follow_mode.keys())
        idx = self.view.row_follow_mode.get_selected()
        val = None
        try:
            val = options[idx]
        except IndexError:
            print("error")
            return
        self.settings.set_value("preferences", "follow_mode", val)


class PageFontColorView(Adw.PreferencesPage):

    def __init__(self, parent_window):
        Adw.PreferencesPage.__init__(self)
        self.set_icon_name('color-symbolic')
        self.get_style_context().add_class('adw-preferences-page')

        self.preview_wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.preview_wrapper.get_style_context().add_class('preview')
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(160)
        scrolled_window.set_propagate_natural_height(True)
        self.source_view = GtkSource.View()
        self.source_view.set_can_focus(False)
        self.source_view.get_style_context().add_class('preview_textview')
        self.source_view.set_editable(False)
        self.source_view.set_cursor_visible(False)
        self.source_view.set_monospace(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(False)
        self.source_view.set_highlight_current_line(False)
        self.source_view.set_left_margin(0)
        scrolled_window.set_child(self.source_view)
        self.source_buffer = self.source_view.get_buffer()
        self.source_buffer.set_highlight_matching_brackets(False)
        self.source_buffer.set_text('''% Syntax highlighting preview
\\documentclass[letterpaper,11pt]{article}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\begin{document}
\\section{Preview}
This is a \\textit{preview}, for $x, y \\in \\mathbb{R}: x \\leq y$ or $x > y$.
\\end{document}''')
        self.source_buffer.place_cursor(self.source_buffer.get_start_iter())
        self.preview_wrapper.append(scrolled_window)

        self.row_preview = Adw.PreferencesRow()
        self.row_preview.set_activatable(False)
        self.row_preview.set_can_focus(False)
        self.row_preview.set_child(self.preview_wrapper)
        self.row_preview.set_focusable(False)

        color_group = Adw.PreferencesGroup()
        color_group.set_title(_("Preview"))
        color_group.add(self.row_preview)

        self.dict_option_follow_mode = dict()
        self.dict_option_follow_mode["manual"] = [_("Manually Set")]
        self.dict_option_follow_mode["system"] = [_("Follow System")]

        combo_model_follow_mode = Gtk.StringList()

        for id in self.dict_option_follow_mode:
            name = self.dict_option_follow_mode[id][0]
            combo_model_follow_mode.append(name)

        self.row_follow_mode = Adw.ComboRow()
        self.row_follow_mode.set_title(_("_Application Style"))
        self.row_follow_mode.set_use_underline(True)
        self.row_follow_mode.set_model(combo_model_follow_mode)

        theme_mode_group = Adw.PreferencesGroup()
        theme_mode_group.set_title(_("Color Schemes"))
        theme_mode_group.add(self.row_follow_mode)

        self.style_switcher = StyleSwitcher()

        scheme_group = Adw.PreferencesGroup()
        scheme_group.add(self.style_switcher)

        self.option_use_custom_font = Gtk.Switch()
        self.option_use_custom_font.set_can_focus(False)
        self.option_use_custom_font.set_valign(Gtk.Align.CENTER)

        self.font_chooser_button = FontChooserButton(parent_window)
        self.font_chooser_button.set_valign(Gtk.Align.CENTER)
        self.font_chooser_button.add_css_class('flat')

        self.subrow_use_font = Adw.ActionRow()
        self.subrow_use_font.set_title(_("_Fonts"))
        self.subrow_use_font.set_use_underline(True)
        self.subrow_use_font.set_subtitle(_("The font used within the editor"))
        self.subrow_use_font.add_suffix(self.font_chooser_button)
        self.subrow_use_font.set_activatable_widget(self.font_chooser_button)

        self.row_use_custom_font = Adw.ExpanderRow()
        self.row_use_custom_font.set_title(_("_Custom Font"))
        self.row_use_custom_font.set_use_underline(True)
        self.row_use_custom_font.bind_property('expanded', self.option_use_custom_font, 'active', GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)
        self.row_use_custom_font.add_action(self.option_use_custom_font)
        self.row_use_custom_font.add_row(self.subrow_use_font)

        font_group = Adw.PreferencesGroup()
        font_group.set_title(_("Fonts"))
        font_group.add(self.row_use_custom_font)

        self.add(color_group)
        self.add(theme_mode_group)
        self.add(scheme_group)
        self.add(font_group)


class StyleSwitcher(Gtk.FlowBox):

    def __init__(self):
        Gtk.FlowBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_row_spacing(6)
        self.set_max_children_per_line(3)
        self.set_homogeneous(True)
        self.set_activate_on_single_click(True)
        self.get_style_context().add_class('theme_previews')

        self.positions = dict()
        self.current_max = 0
        self.current_index = None

        self.connect('selected-children-changed', self.on_child_activated)

    def add_style(self, name):
        style_manager = ServiceLocator.get_source_style_scheme_manager()
        widget = GtkSource.StyleSchemePreview.new(style_manager.get_scheme(name))
        self.append(widget)
        self.positions[name] = self.current_max
        self.current_max += 1

    def select_style(self, name):
        self.select_child(self.get_child_at_index(self.positions[name]))

    def on_child_activated(self, switcher):
        if self.current_index is not None:
            self.get_child_at_index(self.current_index).get_child().set_selected(False)

        child_widget = self.get_selected_children()[0]
        name = child_widget.get_child().get_scheme().get_name()
        child_widget.get_child().set_selected(True)
        self.current_index = self.positions[name]
