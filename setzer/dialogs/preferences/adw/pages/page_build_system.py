import subprocess
import os
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Xdp', '1.0')
from gi.repository import Gtk, Adw, Xdp, GObject


class PageBuildSystem(object):

    def __init__(self, preferences, settings):
        self.view = PageBuildSystemView()
        self.preferences = preferences
        self.settings = settings
        self.latex_interpreters = list()
        self.latexmk_available = False
        self.handle_latex_int_map = dict()

    def init(self):
        self.view.option_cleanup_build_files.set_active(
            self.settings.get_value("preferences", "cleanup_build_files"),
        )
        self.view.option_cleanup_build_files.connect("notify::active", self.on_switch_flipped, self.view.option_cleanup_build_files, "cleanup_build_files")

        self.view.option_use_latexmk.set_active(
            self.settings.get_value("preferences", "use_latexmk"),
        )
        self.view.option_use_latexmk.connect("notify::active", self.on_switch_flipped, self.view.option_use_latexmk, "use_latexmk")

        self.view.row_autoshow_build_log.set_selected(
            self.get_enum_idx_from_dict("autoshow_build_log", self.view._option_autoshow_build_log)
        )

        self.view.row_autoshow_build_log.connect(
            "notify::selected",
            self.update_enum_from_dict,
            "autoshow_build_log",
            self.view._option_autoshow_build_log,
            self.view.row_autoshow_build_log
        )

        self.view.row_system_commands.set_selected(
            self.get_enum_idx_from_dict("build_option_system_commands", self.view._options_system_commands)
        )

        self.view.row_system_commands.connect(
            "notify::selected",
            self.update_enum_from_dict,
            "build_option_system_commands",
            self.view._options_system_commands,
            self.view.row_system_commands
        )

        self.setup_latex_interpreters()
        self.update_row_latex_interpreter()

    def handle_latex_int_map_default(self):
        self.view.no_interpreter_label.hide()
        self.view.tectonic_warning_label.hide()
        self.view.row_use_latexmk.show()
        self.view.row_system_commands.show()

    def handle_latex_int_map_no_int(self):
        self.view.no_interpreter_label.show()
        self.view.tectonic_warning_label.hide()
        self.view.row_use_latexmk.show()
        self.view.row_system_commands.show()

    def handle_latex_int_map_tectonic(self):
        self.view.no_interpreter_label.hide()
        self.view.tectonic_warning_label.show()
        self.view.row_use_latexmk.hide()
        self.view.row_system_commands.hide()

    def setup_latex_interpreters(self):
        for interpreter in ["xelatex", "pdflatex", "lualatex", "tectonic"]:
            arguments = [interpreter, '--version']
            try:
                process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                pass
            else:
                process.wait()
                if process.returncode == 0:
                    self.latex_interpreters.append(interpreter)

        self.combo_index_2_id = []
        for id in self.view.option_latex_interpreter:
            if id in self.latex_interpreters:
                name = self.view.option_latex_interpreter[id][0]
                self.view.combo_options_latex_interpreter.append(name)
                self.combo_index_2_id.append(id)

        self.handle_latex_int_map["tectonic"] = self.handle_latex_int_map_tectonic

        self.view.latex_int_combobox.connect(
            "notify::selected",
            self.update_row_latex_interpreter
        )

        self.view.latex_int_combobox.set_selected(
            self.get_enum_idx_from_dict("latex_interpreter", self.view.option_latex_interpreter)
        )

        self.view.latex_int_combobox.connect(
            "notify::selected",
            self.update_enum_from_arr,
            "latex_interpreter",
            self.combo_index_2_id,
            self.view.latex_int_combobox
        )

    def update_row_latex_interpreter(self, arg1=None, arg2=None):
        handler = 0
        if len(self.latex_interpreters) <= 0:
            return self.handle_latex_int_map_no_int
        else:
            idx = self.view.latex_int_combobox.get_selected()
            id = 0
            try:
                id = self.combo_index_2_id[idx]
                handler = self.handle_latex_int_map[id]
            except (IndexError, KeyError):
                pass
        if handler == 0:
            handler = self.handle_latex_int_map_default
        handler()

    def get_enum_idx_from_dict(self, preferences_name, dictionary, *args):
        val = self.settings.get_value(
          "preferences",
          preferences_name,
        )
        options = list(dictionary.keys())
        idx = -1
        try:
            idx = options.index(val)
        except ValueError:
            idx = 0
        return idx

    def update_enum_from_dict(self, object, selected, preferences_name, dictionary, combobox, *args):
        options = list(dictionary.keys())
        idx = combobox.get_selected()
        val = None
        try:
            val = options[idx]
        except IndexError:
            print("error")
            val = 0
        self.settings.set_value("preferences", preferences_name, val)

    def update_enum_from_arr(self, object, pspec, preferences_name, arr, combobox, *args):
        options = list(arr)
        idx = combobox.get_selected()
        val = None
        try:
            val = options[idx]
        except IndexError:
            print("error")
            val = 0
        self.settings.set_value("preferences", preferences_name, val)

    def on_switch_flipped(self, object, pspec, button, preference_name):
        self.settings.set_value(
            "preferences",
            preference_name,
            button.get_active(),
        )


class PageBuildSystemView(Adw.PreferencesPage):

    def __init__(self):
        Adw.PreferencesPage.__init__(self)
        self.set_icon_name("builder-build-symbolic")
        # self.set_title("Build System")

        self.option_latex_interpreter = dict()
        self.option_latex_interpreter['xelatex'] = ["XeLaTeX"]
        self.option_latex_interpreter['pdflatex'] = ["PdfLaTeX"]
        self.option_latex_interpreter['lualatex'] = ["LuaLaTeX"]
        self.option_latex_interpreter['tectonic'] = ["Tectonic"]
        self.combo_options_latex_interpreter = Gtk.StringList()

        self.latex_int_combobox = Adw.ComboRow()
        self.latex_int_combobox.set_title(_("LaTeX Interpreter"))
        self.latex_int_combobox.set_model(self.combo_options_latex_interpreter)

        self.no_interpreter_label = Gtk.Label()
        self.no_interpreter_label.set_wrap(True)
        self.no_interpreter_label.set_xalign(0)
        self.no_interpreter_label.set_margin_top(12)
        self.no_interpreter_label.add_css_class("dim-label")
        self.no_interpreter_label.add_css_class("caption")
        self.no_interpreter_label.set_label(_('''No LaTeX interpreter found. To install interpreters in Flatpak, open a terminal and run the following command:
    flatpak install org.freedesktop.Sdk.Extension.texlive'''))

        self.tectonic_warning_label = Gtk.Label()
        self.tectonic_warning_label.set_wrap(True)
        self.tectonic_warning_label.set_xalign(0)
        self.tectonic_warning_label.set_margin_top(12)
        self.tectonic_warning_label.add_css_class("dim-label")
        self.tectonic_warning_label.add_css_class("caption")
        self.tectonic_warning_label.set_label(
          _("Please note: the Tectonic backend uses only the V1 command-line interface. Tectonic.toml configuration files are ignored."),
        )

        first_group = Adw.PreferencesGroup()
        first_group.add(self.latex_int_combobox)
        first_group.add(self.no_interpreter_label)
        first_group.add(self.tectonic_warning_label)

        self.option_cleanup_build_files = Gtk.Switch()
        self.option_cleanup_build_files.set_focusable(False)
        self.option_cleanup_build_files.set_valign(Gtk.Align.CENTER)

        self.row_cleanup_build_files = Adw.ActionRow()
        self.row_cleanup_build_files.set_title(_("Cleanup After Building"))
        self.row_cleanup_build_files.set_subtitle(
          _("Automatically remove helper files (.log, .dvi, …) after building .pdf."),
        )
        self.row_cleanup_build_files.add_suffix(self.option_cleanup_build_files)
        self.row_cleanup_build_files.set_activatable_widget(self.option_cleanup_build_files)

        self.option_use_latexmk = Gtk.Switch()
        self.option_use_latexmk.set_focusable(False)
        self.option_use_latexmk.set_valign(Gtk.Align.CENTER)

        self.row_use_latexmk = Adw.ActionRow()
        self.row_use_latexmk.set_title(_("Use Latexmk"))
        self.row_use_latexmk.add_suffix(self.option_use_latexmk)
        self.row_use_latexmk.set_activatable_widget(self.option_use_latexmk)

        second_group = Adw.PreferencesGroup()
        second_group.set_title(_("Options"))
        second_group.add(self.row_cleanup_build_files)
        second_group.add(self.row_use_latexmk)

        self.option_autoshow_build_log = Gtk.StringList()

        self._option_autoshow_build_log = dict()
        self._option_autoshow_build_log['errors'] = [_("Errors")]
        self._option_autoshow_build_log['errors_warning'] = [_("Errors + Warnings")]
        self._option_autoshow_build_log['all'] = [_("All")]

        for id in self._option_autoshow_build_log:
            name = self._option_autoshow_build_log[id][0]
            self.option_autoshow_build_log.append(name)

        self.row_autoshow_build_log = Adw.ComboRow()
        self.row_autoshow_build_log.set_title(_("Show Build Log"))
        self.row_autoshow_build_log.set_model(self.option_autoshow_build_log)

        self._options_system_commands = dict()
        self._options_system_commands['disable'] = [_("Disabled")]
        self._options_system_commands['restricted'] = [_("Enabled (Restricted)")]
        self._options_system_commands['enable'] = [_("Enabled (Full)")]

        self.option_system_commands = Gtk.StringList()
        for id in self._options_system_commands:
            name = self._options_system_commands[id][0]
            self.option_system_commands.append(name)

        self.row_system_commands = Adw.ComboRow()
        self.row_system_commands.set_title(_("Embedded System Commands"))
        self.row_system_commands.set_subtitle(
          _("Enable this only if you have to. It can cause security problems when building files from untrusted sources."),
        )
        self.row_system_commands.set_model(self.option_system_commands)

        third_group = Adw.PreferencesGroup()
        third_group.add(self.row_autoshow_build_log)
        third_group.add(self.row_system_commands)

        self.add(first_group)
        self.add(second_group)
        self.add(third_group)
