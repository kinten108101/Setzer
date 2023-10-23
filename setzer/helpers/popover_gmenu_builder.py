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
import inspect


handler_placeholder = 'placeholder'


def is_same_function(target, name, argc):
    if target.__name__ == name and len(inspect.getfullargspec(target).args) == argc:
        return True
    else:
        return False


class PriorityQueue(list):

    first_group_top = 0

    def append(self, item, priority=0):
        if priority == 1:
            super().append(item)
        else:
            super().insert(self.first_group_top, item)
            self.first_group_top += 1


class MenuItem(Gio.MenuItem):

    action_name = None

    def set_detailed_action(self, name):
        super().set_detailed_action(name)
        self.action_name = name
        if hasattr(self, 'reload'):
            self.reload()

    def set_action_name(self, name):
        self.set_detailed_action(name)

    def set_action_target_value(self, value):
        if self.action_name is not None:
            super().set_action_and_target_value(self.action_name, value)
            if hasattr(self, 'reload'):
                self.reload()

    def set_icon_name(self, name):
        pass

    def connect(self, signal, callback, *args):
        if signal == 'clicked':
            if is_same_function(callback, 'show_page', 4):
                _args = args
                assert len(_args) == 1 or len(_args) == 2
                pagename = _args[0]
                # We must rely on callback to get self object, it's the only parameter that has any relation to the menu object.
                # As for the how, we modify show_page. PopoverMenu.show_page should return itself.
                # If only there's a better way.
                # Only PopoverMenu.show_page does this. If it's not PopoverMenu then we cannot continue
                menu = callback(self, *args)
                if menu is None:
                    return handler_placeholder
                MenuBuilder.link_to_menu(menu, self, pagename)
                return handler_placeholder
            return self.connect_clicked(callback, *args)
        else:
            super().connect(signal, callback, *args)

    def connect_clicked(self, callback, *args):
        if self.action_name is not None:
            print('You attempted to override actionable with click signal handler. Not allowed here, please use the GioAction API.')
            return handler_placeholder
        window = ServiceLocator.get_main_window()
        if window is None:
            print('Adding actions too early')
            return handler_placeholder
        if not hasattr(self, 'callbacks'):
            self.callbacks = list()
            name = 'menu.' + str(generate_id())
            action = Gio.SimpleAction.new(name, None)
            action.connect('activate', self.on_stateless_action_activate, *args)
            window.app.add_action(action)
            detailed_name = 'app.' + name
            self.set_detailed_action(detailed_name)
        self.callbacks.append(callback)
        return handler_placeholder

    def disconnect(self, handler):
        if handler is handler_placeholder:
            return
        else:
            super().disconnect(handler)

    def on_stateless_action_activate(self, action, *args):
        for fn in self.callbacks:
            fn(*args)


class Menu(Gio.Menu):

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


class PopoverMenu(Gtk.PopoverMenu):

    def __init__(self):
        Gtk.PopoverMenu.__init__(self)
        model = Menu()
        self.set_menu_model(model)
        current_section = Menu()
        model.append_section(None, current_section)
        self.page_map = dict()
        self.page_map['main'] = (model, current_section, None)

    def show_page(self, button, pagename, transition_type):
        return self


prev_id = 0


def generate_id():
    global prev_id
    prev_id = prev_id + 1
    return prev_id


class MenuBuilder():

    def create_menu():
        menu = PopoverMenu()
        return menu

    def create_button(label, icon_name=None, shortcut=None):
        item = MenuItem()
        if label is not None:
            item.set_label(label)
        if icon_name is not None:
            item.set_icon_name(icon_name)
        return item

    def create_button_widget(label, icon_name=None, shortcut=None):
        item = Gtk.Button()
        item.get_style_context().add_class('flat')
        if label is not None:
            item.set_label(label)
        if icon_name is not None:
            item.set_icon_name(icon_name)
        return item

    def create_menu_button(label):
        item = MenuItem()
        if (label != None): item.set_label(label)
        return item

    def add_page(menu, pagename, label):
        model = Menu()
        current_section = Menu()
        model.append_section(None, current_section)
        try:
            page = menu.page_map[pagename]
        except KeyError:
            page = None
        if page is None:
            data = (model, current_section, None)
        else:
            assert page[0] is None and page[1] is None and page[2] is not None
            data = (model, current_section, page[2])
        menu.page_map[pagename] = data
        MenuBuilder.build_page(menu, pagename)

    def link_to_menu(menu, item, pagename):
        def setup_fn(_page):
            assert _page is not None
            model = _page[0]
            item.set_submenu(model)
            if hasattr(item, 'reload'):
                item.reload()
            print('Linking to page {pagename}'.format(pagename=pagename))
        MenuBuilder.process_setup_fn(menu, pagename, setup_fn, 1)

    def process_setup_fn(menu, pagename, setup_fn, priority=0):
        page = menu.page_map.get(pagename)

        if page is None:
            setup_fns = PriorityQueue()
            page = (None, None, setup_fns)
        setup_fns = page[2]
        if setup_fns is None:
            setup_fns = PriorityQueue()
        setup_fns.append(setup_fn, priority)
        data = (page[0], page[1], setup_fns)
        menu.page_map[pagename] = data
        if data[0] is not None and data[1] is not None:
            setup_fn(data)

    def add_item(menu, item, pagename='main'):
        def setup_fn(_page):
            assert _page is not None
            current_section = _page[1]
            current_section.append_item(item)

        MenuBuilder.process_setup_fn(menu, pagename, setup_fn)

    def add_widget(menu, widget, pagename='main'):
        if isinstance(widget, Gio.MenuItem):
            return MenuBuilder.add_item(menu, widget, pagename)
        else:
            return MenuBuilder.add_custom_widget(menu, widget, pagename)

    def add_custom_widget(menu, widget, pagename='main'):
        def setup_fn(_page):
            current_section = _page[1]
            item = MenuItem()
            id = str(generate_id())
            item.set_attribute_value('custom', GLib.Variant('s', id))
            current_section.append_item(item)
            menu.add_child(widget, id)
        MenuBuilder.process_setup_fn(menu, pagename, setup_fn)

    def add_separator(menu, pagename='main'):
        def setup_fn(_page):
            model = _page[0]
            new_section = Menu()
            model.append_section(None, new_section)
            menu.page_map[pagename] = (model, new_section, _page[2])
        MenuBuilder.process_setup_fn(menu, pagename, setup_fn)

    def build_page(menu, pagename):
        page = menu.page_map[pagename]
        assert page is not None
        assert page[0] is not None
        assert page[1] is not None
        if page[2] is None:
            return
        for fn in page[2]:
            fn(page)
