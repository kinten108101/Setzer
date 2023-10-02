import gi
from gi.repository import Adw


class AboutDialog(object):

    def __init__(self):
        self.window = Adw.AboutWindow()

    def set_transient_for(self, window):
        self.window.set_transient_for(window)

    def set_modal(self, val):
        self.window.set_modal(val)

    def set_program_name(self, name):
        self.window.set_application_name(name)

    def set_version(self, version):
        self.window.set_version(version)

    def set_copyright(self, text):
        self.window.set_copyright(text)

    def set_comments(self, comments):
        self.window.set_comments(comments)

    def set_license_type(self, license_type):
        self.window.set_license_type(license_type)

    def set_website(self, website):
        self.window.set_website(website)

    def set_website_label(self, label):
        pass

    def set_authors(self, authors):
        self.window.set_developers(authors)

    def set_logo_icon_name(self, icon_name):
        self.window.set_application_icon(icon_name)

    def set_translator_credits(self, val):
        self.window.set_translator_credits(val)

    def show(self):
        self.window.show()
