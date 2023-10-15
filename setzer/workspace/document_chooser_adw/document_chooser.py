import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib, GObject, Gtk, Gio
import os.path
from setzer.app.service_locator import ServiceLocator


class DocumentChooserEntry(GObject.Object):

    def __init__(self, file_dir, file_name):
        GObject.Object.__init__(self)
        self.file_name = file_name
        self.file_dir = file_dir


class DocumentChooser(GObject.Object):

    search_string = GObject.Property(type=str, default="")

    def __init__(self, workspace):
        super().__init__()
        self.workspace = workspace
        self.main_widnow = ServiceLocator.get_main_window()
        self.recently_opened_documents = Gio.ListStore()
        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)
        self.view = ServiceLocator.get_main_window().headerbar.document_chooser
        self.view.factory.connect("bind", self.on_popover_listview_factory_bind)
        self.view.search_entry.connect('changed', self.on_search_entry_changed)
        self.view.search_entry.connect('stop-search', self.on_stop_search)

        self.on_recently_opened_documents_changed(self.recently_opened_documents)
        self.recently_opened_documents.connect("notify::n-items", self.on_recently_opened_documents_changed)
        self.connect("notify::search-string", self.on_search_string_changed)
        self.filter = Gtk.CustomFilter.new(self.filter_match_func)
        self.model = Gtk.FilterListModel.new(self.recently_opened_documents, self.filter)
        self.on_filtered_recent_list_changed(self.model)
        self.model.connect('notify::n-items', self.on_filtered_recent_list_changed)
        self.view.list.set_model(Gtk.NoSelection.new(self.model))
        self.view.other_documents_button.connect('clicked', self.on_other_docs_clicked)
        self.view.list.connect('activate', self.on_listview_row_activate)

    def on_popover_listview_factory_bind(self, object, listitem):
        child = listitem.get_child()
        item = listitem.get_item()

        child.file_name.set_label(item.file_name)

        home_dir = GLib.get_home_dir()
        file_dir = item.file_dir
        if home_dir is not None:
            file_dir = item.file_dir.replace(home_dir, "~")
        child.file_dir.set_label(file_dir)

        child.set_tooltip_text(item.file_dir + '/' + item.file_name)

    def on_search_entry_changed(self, object):
        self.search_string = object.get_text()

    def on_recently_opened_documents_n_items_2_search_entry_sensitive(self, object, fromval):
        if fromval == 0:
            return [True, False]
        return [True, True]

    def on_recently_opened_documents_changed(self, object, pspec=None):
        n = object.get_n_items()
        if n <= 0:
            self.view.set_visible_child_name('empty')
            self.view.search_entry.set_visible(False)
        else:
            self.view.search_entry.set_visible(True)

    def on_search_string_changed(self, object, pspec):
        self.filter.changed(Gtk.FilterChange.DIFFERENT)

    def on_stop_search(self, search_entry):
        self.view.popdown()

    def filter_match_func(self, item) -> bool:
        path = item.file_dir + '/' + item.file_name
        if self.search_string in path:
            return True
        return False

    def on_filtered_recent_list_changed(self, object, pspec=None):
        n = object.get_n_items()
        if self.recently_opened_documents.get_n_items() <= 0:
            return
        if n <= 0:
            self.view.set_visible_child_name('noresult')
        else:
            self.view.set_visible_child_name('mainpage')

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        self.recently_opened_documents.remove_all()
        data = recently_opened_documents.values()
        for item in sorted(data, key=lambda val: -val['date']):
            filesplit = os.path.split(item['filename'])
            gitem = DocumentChooserEntry(filesplit[0], filesplit[1])
            self.recently_opened_documents.append(gitem)

    def on_other_docs_clicked(self, button):
        self.workspace.actions.actions['open-document-dialog'].activate()
        self.view.popdown()

    def on_listview_row_activate(self, listview, position):
        item = self.model.get_item(position)
        self.view.popdown()
        filename = item.file_dir + '/' + item.file_name
        self.workspace.open_document_by_filename(filename)
