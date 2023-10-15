import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango


class DocumentChooserEntry(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_halign(Gtk.Align.FILL)
        self.set_hexpand(True)
        self.set_spacing(8)
        vbox_left = Gtk.Box()
        vbox_left.set_halign(Gtk.Align.FILL)
        vbox_left.set_hexpand(True)
        vbox_left.set_orientation(Gtk.Orientation.VERTICAL)

        self.file_name = Gtk.Label()
        self.file_name.set_halign(Gtk.Align.START)
        self.file_name.set_ellipsize(Pango.EllipsizeMode.END)
        self.file_name.get_style_context().add_class("file_name")
        vbox_left.append(self.file_name)

        self.file_dir = Gtk.Label()
        self.file_dir.set_halign(Gtk.Align.START)
        self.file_dir.set_ellipsize(Pango.EllipsizeMode.END)
        self.file_dir.get_style_context().add_class("dim-label")
        self.file_dir.get_style_context().add_class("file_path")
        vbox_left.append(self.file_dir)

        self.append(vbox_left)

        vbox_right = Gtk.Box()
        vbox_right.set_orientation(Gtk.Orientation.VERTICAL)
        vbox_right.set_valign(Gtk.Align.CENTER)

        remove = Gtk.Button()
        remove.set_icon_name("cross-symbolic")
        remove.set_tooltip_text(_("Remove"))
        remove.get_style_context().add_class("flat")
        remove.get_style_context().add_class("circular")
        vbox_right.append(remove)

        self.append(vbox_right)


class DocumentChooser(Gtk.Popover):

    ''' GNOME Text Editor-like document chooser widget '''

    def __init__(self):
        Gtk.Popover.__init__(self)
        self.pages = dict()
        self.get_style_context().add_class("documentchooser_adw")
        self.set_size_request(450, -1)
        self.set_offset(75, 0)
        vbox = Gtk.Box()
        vbox.set_orientation(Gtk.Orientation.VERTICAL)

        vvbox = Gtk.Box()
        vvbox.set_orientation(Gtk.Orientation.VERTICAL)

        tophbox = Gtk.Box()
        tophbox.set_spacing(6)
        tophbox.set_margin_top(6)
        tophbox.set_margin_start(6)
        tophbox.set_margin_end(6)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_hexpand(True)
        self.search_entry.set_placeholder_text(_("Search documents"))
        self.search_entry.set_tooltip_text(_("Recently Used Documents"))
        tophbox.append(self.search_entry)

        self.other_documents_button = Gtk.Button()
        self.other_documents_button.set_tooltip_text(_("Open Other Documents") + " (" + _("Ctrl + O") + ")")
        self.other_documents_button.set_icon_name("document-open-symbolic")
        tophbox.append(self.other_documents_button)

        vvbox.append(tophbox)
        separator = Gtk.Separator()
        vvbox.append(separator)
        vbox.append(vvbox)

        self.stack = Gtk.Stack()
        vbox.append(self.stack)
        self.set_child(vbox)

        self.setup_mainpage()
        self.setup_noresult()
        self.setup_empty()

    def setup_mainpage(self):
        mainpage_box = Gtk.Box()
        scroller = Gtk.ScrolledWindow()
        scroller.set_hexpand(True)
        scroller.set_max_content_height(600)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        scroller.set_propagate_natural_height(True)
        scroller.set_vexpand(True)
        viewport = Gtk.Viewport()
        scroller.set_child(viewport)
        self.list = Gtk.ListView()
        self.list.set_single_click_activate(True)
        self.list.set_margin_top(0)
        self.list.set_margin_end(6)
        self.list.set_margin_start(6)
        self.list.get_style_context().add_class("navigation-sidebar")
        viewport.set_child(self.list)
        mainpage_box.append(scroller)

        self.factory = Gtk.SignalListItemFactory()
        self.factory.connect("setup", self.on_listview_factory_setup)
        self.list.set_factory(self.factory)

        mainpage = self.stack.add_child(mainpage_box)
        self.pages["mainpage"] = mainpage_box
        mainpage.set_name("mainpage")

    def setup_noresult(self):
        noresult_box = Gtk.Box()
        noresult_box.set_halign(Gtk.Align.CENTER)
        noresult_box.set_valign(Gtk.Align.CENTER)

        content = Gtk.Box()
        content.get_style_context().add_class("noresult_content")
        no_result = Gtk.Label()
        no_result.set_label("No Results Found")
        no_result.get_style_context().add_class("dim-label")
        content.append(no_result)
        noresult_box.append(content)

        noresult = self.stack.add_child(noresult_box)
        self.pages["noresult"] = noresult_box
        noresult.set_name("noresult")

    def setup_empty(self):
        empty_box = Gtk.Box()
        empty_box.set_orientation(Gtk.Orientation.VERTICAL)
        empty_box.set_halign(Gtk.Align.CENTER)
        empty_box.set_valign(Gtk.Align.CENTER)

        content = Gtk.Box()
        content.set_orientation(Gtk.Orientation.VERTICAL)
        content.set_halign(Gtk.Align.CENTER)
        content.set_valign(Gtk.Align.CENTER)
        content.get_style_context().add_class("empty_page_content")
        icon = Gtk.Image()
        icon.set_from_icon_name("document-open-recent-symbolic")
        icon.set_icon_size(Gtk.IconSize.LARGE)
        icon.get_style_context().add_class("dim-label")
        content.append(icon)
        text = Gtk.Label()
        text.set_label(_("No Recent Documents"))
        text.set_wrap(True)
        text.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text.get_style_context().add_class("dim-label")
        content.append(text)
        empty_box.append(content)

        empty = self.stack.add_child(empty_box)
        self.pages["empty"] = empty_box
        empty.set_name("empty")

    def on_listview_factory_setup(self, object, listitem):
        widget = DocumentChooserEntry()
        listitem.set_child(widget)

    def set_visible_child_name(self, name):
        self.stack.set_visible_child_name(name)
        for key in self.pages:
            x = self.pages[key]
            if (key == name):
                x.set_visible(True)
            else:
                x.set_visible(False)
