#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
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
from gi.repository import Gdk
from gi.repository import Gio

from setzer.widgets.scrolling_widget.scrolling_widget import ScrollingWidget


class PreviewView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview')

        self.action_bar = Gtk.CenterBox()
        self.action_bar.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.action_bar.set_size_request(-1, 37)

        self.action_bar_left = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.action_bar.set_start_widget(self.action_bar_left)
        self.action_bar_right = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.action_bar.set_end_widget(self.action_bar_right)

        self.external_viewer_button = Gtk.Button.new_from_icon_name('external-viewer-symbolic')
        self.external_viewer_button.set_tooltip_text(_('External Viewer'))
        self.external_viewer_button.get_style_context().add_class('flat')
        self.external_viewer_button.set_can_focus(False)
        self.external_viewer_button.get_style_context().add_class('scbar')
        self.external_viewer_button_revealer = Gtk.Revealer()
        self.external_viewer_button_revealer.set_transition_type(Gtk.RevealerTransitionType.NONE)
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.append(self.external_viewer_button)
        self.external_viewer_button_revealer.set_child(box)
        self.action_bar_right.append(self.external_viewer_button_revealer)

        self.append(self.action_bar)

        self.content = ScrollingWidget()
        self.drawing_area = self.content.content

        self.blank_slate = BlankSlateView()

        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.add_named(self.blank_slate, 'blank_slate')
        self.stack.add_named(self.content.view, 'pdf')
        self.append(self.stack)

    def set_layout_data(self, layout_data):
        self.layout_data = layout_data


class BlankSlateView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class('preview_blank')

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_vexpand(True)
        self.append(drawing_area)

        image = Gtk.Image.new_from_icon_name('own-no-preview-symbolic')
        image.set_pixel_size(150)
        self.append(image)

        header = Gtk.Label.new(_('No preview available'))
        header.get_style_context().add_class('header')
        self.append(header)

        body = Gtk.Label.new(_('To show a .pdf preview of your document, click the build button in the headerbar.'))
        body.get_style_context().add_class('body')
        body.set_wrap(True)
        self.append(body)

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_vexpand(True)
        self.append(drawing_area)


