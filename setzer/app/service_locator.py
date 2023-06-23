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
gi.require_version('GtkSource', '5')
from gi.repository import GtkSource
from gi.repository import GLib

import re
import os, os.path

import setzer.app.settings as settingscontroller
from setzer.app.color_manager import ColorManager


class ServiceLocator(object):

    main_window = None
    workspace = None
    settings = None
    setzer_version = None
    resources_path = None
    app_icons_path = None
    regexes = dict()
    source_language_manager = None
    source_style_scheme_manager = None

    def set_main_window(main_window):
        ServiceLocator.main_window = main_window

    def get_main_window():
        return ServiceLocator.main_window

    def set_workspace(workspace):
        ServiceLocator.workspace = workspace

    def get_workspace():
        return ServiceLocator.workspace

    def get_regex_object(pattern):
        try:
            regex = ServiceLocator.regexes[pattern]
        except KeyError:
            regex = re.compile(pattern)
            ServiceLocator.regexes[pattern] = regex
        return regex

    def get_settings():
        if ServiceLocator.settings == None:
            ServiceLocator.settings = settingscontroller.Settings(ServiceLocator.get_config_folder())
        return ServiceLocator.settings

    def get_config_folder():
        return os.path.join(GLib.get_user_config_dir(), 'setzer')

    def set_setzer_version(setzer_version):
        ServiceLocator.setzer_version = setzer_version

    def get_setzer_version():
        return ServiceLocator.setzer_version

    def set_resources_path(resources_path):
        ServiceLocator.resources_path = resources_path

    def get_resources_path():
        return ServiceLocator.resources_path

    def set_app_icons_path(app_icons_path):
        ServiceLocator.app_icons_path = app_icons_path

    def get_app_icons_path():
        return ServiceLocator.app_icons_path

    def get_is_dark_mode():
        fg_color = ColorManager.get_ui_color('theme_fg_color')
        bg_color = ColorManager.get_ui_color('theme_bg_color')
        return (fg_color.red + fg_color.green + fg_color.blue) * fg_color.alpha > (bg_color.red + bg_color.green + bg_color.blue) * bg_color.alpha

    def get_source_language_manager():
        if ServiceLocator.source_language_manager == None:
            ServiceLocator.source_language_manager = GtkSource.LanguageManager()
            path = os.path.join(ServiceLocator.get_resources_path(), 'gtksourceview', 'language-specs')
            ServiceLocator.source_language_manager.set_search_path((path,))
        return ServiceLocator.source_language_manager

    def get_source_style_scheme_manager():
        if ServiceLocator.source_style_scheme_manager == None:
            ServiceLocator.source_style_scheme_manager = GtkSource.StyleSchemeManager()
            path1 = os.path.join(ServiceLocator.get_resources_path(), 'gtksourceview', 'styles')
            if not os.path.isdir(os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')):
                os.mkdir(os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes'))
            path2 = os.path.join(ServiceLocator.get_config_folder(), 'syntax_schemes')
            ServiceLocator.source_style_scheme_manager.set_search_path((path1, path2))
        return ServiceLocator.source_style_scheme_manager

    def get_source_language(language):
        source_language_manager = ServiceLocator.get_source_language_manager()
        if language == 'bibtex': return source_language_manager.get_language('bibtex')
        else: return source_language_manager.get_language('latex')

    def get_style_scheme():
        if ServiceLocator.get_is_dark_mode():
            name = ServiceLocator.get_settings().get_value('preferences', 'syntax_scheme_dark_mode')
        else:
            name = ServiceLocator.get_settings().get_value('preferences', 'syntax_scheme')
        return ServiceLocator.get_source_style_scheme_manager().get_scheme(name)


