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
from setzer.app.service_locator import ServiceLocator


class MenuItemTest(Gio.MenuItem):

    def set_detailed_action(self, name):
        super().set_detailed_action(name)
        if hasattr(self, 'reload'):
            self.reload()

    def connect(self, signal, callback):
        if signal == 'clicked':
            name = 'menu.' + str(generate_id())
            print('MenuItemTest::connect::clicked: ' + name)
            action = Gio.SimpleAction.new(name, None)

            def on_action_activate(self, action):
                callback(self)

            action.connect('activate', on_action_activate)
            ServiceLocator.get_main_window().app.add_action(action)
            detailed_name = 'app.' + name
            self.set_detailed_action(detailed_name)


class MenuTest(Gio.Menu):

    def __init__(self):
        super().__init__()
        self.item_map = dict()
        self.count = 0

    def reload_menuitem(self, menuitem):
        idx = self.item_map[menuitem]
        self.remove(idx)
        self.insert_item(idx, menuitem)

    def insert_item(self, pos, menuitem):
        super().insert_item(pos, menuitem)

        def _reload(_self=None):
            self.reload_menuitem(menuitem)

        menuitem.reload = _reload
        self.item_map[menuitem] = pos
        self.count += 1

    def append_item(self, menuitem):
        super().append_item(menuitem)

        def _reload(_self=None):
            self.reload_menuitem(menuitem)

        menuitem.reload = _reload
        self.item_map[menuitem] = self.count
        self.count += 1


class PopoverMenuTest(Gtk.PopoverMenu):

    def __init__(self):
        Gtk.PopoverMenu.__init__(self)
        model = Gio.Menu()
        self.set_menu_model(model)
        current_section = Gio.Menu()
        model.append_section(None, current_section)
        self.page_map = dict()
        self.page_map['main'] = (model, current_section)


class PopoverMenu(Gtk.Popover):

    def __init__(self):
        Gtk.Popover.__init__(self)

        stack = Gtk.Stack()
        stack.set_vhomogeneous(False)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        stack.add_named(box, 'main')

        self.set_child(stack)

        self.connect('closed', self.on_close)

    def show_page(self, button, page_name, transition_type):
        self.get_child().set_transition_type(transition_type)
        self.get_child().set_visible_child_name(page_name)

    def on_close(self, popover):
        self.show_page(None, 'main', Gtk.StackTransitionType.NONE)


prev_id = 0


def generate_id():
    global prev_id
    prev_id = prev_id + 1
    return prev_id


class MenuBuilderTest():

    def create_menu():
        menu = PopoverMenuTest()
        return menu

    def create_button(label, icon_name=None, shortcut=None):
        item = MenuItemTest()
        if (label != None): item.set_label(label)
        if (icon_name != None): item.set_icon_name(icon_name)
        return item

    def create_menu_button(label):
        item = MenuItemTest()
        if (label != None): item.set_label(label)
        return item

    def add_page(menu, pagename, label):
        model = MenuTest()
        current_section = MenuTest()
        model.append_section(None, current_section)
        menu.page_map[pagename] = (model, current_section)

    def link_to_menu(menu, item, pagename):
        page = menu.page_map.get(pagename)
        assert page is not None
        model = page[0]
        item.set_submenu(model)

    def add_item(menu, item, pagename='main'):
        page = menu.page_map.get(pagename)
        assert page is not None
        current_section = page[1]
        current_section.append_item(item)

    def add_widget(menu, widget, pagename='main'):
        if isinstance(widget, Gio.MenuItem):
            return MenuBuilderTest.add_item(menu, widget, pagename)
        else:
            return MenuBuilderTest.add_custom_widget(menu, widget, pagename)

    def add_custom_widget(menu, widget, pagename='main'):
        page = menu.page_map.get(pagename)
        assert page is not None
        current_section = page[1]
        item = MenuItemTest()
        id = str(generate_id())
        item.set_attribute_value('custom', GLib.Variant('s', id))
        current_section.append_item(item)
        menu.add_child(widget, id)

    def add_separator(menu, pagename='main'):
        page = menu.page_map[pagename]
        assert page is not None
        model = page[0]
        new_section = MenuTest()
        model.append_section(None, new_section)
        menu.page_map[pagename] = (model, new_section)


class MenuBuilder():

    def create_menu():
        menu = PopoverMenu()
        return menu

    def create_button(label, icon_name=None, shortcut=None):
        button = Gtk.Button()
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button.set_child(button_box)
        button.get_style_context().add_class('action')

        if icon_name == 'placeholder':
            icon = Gtk.DrawingArea()
            icon.set_size_request(24, 16)
            button_box.append(icon)
        elif icon_name != None:
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.get_style_context().add_class('icon')
            button_box.append(icon)

        button_box.append(Gtk.Label.new(label))

        if shortcut != None:
            shortcut_label = Gtk.Label.new(shortcut)
            shortcut_label.get_style_context().add_class('shortcut')
            shortcut_label.set_xalign(1)
            shortcut_label.set_hexpand(True)
            button_box.append(shortcut_label)

        return button

    def create_menu_button(label):
        button = Gtk.Button()
        button_box = Gtk.CenterBox()
        button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        button.set_child(button_box)
        button.get_style_context().add_class('menu')

        button_box.set_start_widget(Gtk.Label.new(label))
        button_box.set_end_widget(Gtk.Image.new_from_icon_name('pan-end-symbolic'))

        return button

    def add_page(menu, pagename, label):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        button = Gtk.Button()
        button_box = Gtk.CenterBox()
        button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        button.set_child(button_box)
        button.get_style_context().add_class('header')
        button.connect('clicked', menu.show_page, 'main', Gtk.StackTransitionType.SLIDE_LEFT)

        button_box.set_center_widget(Gtk.Label.new(label))
        button_box.set_start_widget(Gtk.Image.new_from_icon_name('pan-start-symbolic'))
        box.append(button)

        menu.get_child().add_named(box, pagename)

    def add_widget(menu, widget, pagename='main'):
        box = menu.get_child().get_child_by_name(pagename)
        box.append(widget)

    def add_separator(menu, pagename='main'):
        box = menu.get_child().get_child_by_name(pagename)
        box.append(Gtk.Separator.new(Gtk.Orientation.HORIZONTAL))


