from gi.repository import GObject, Gio, Gdk, Gtk, Gedit

class DuplicateLineAppActivatable(GObject.Object, Gedit.AppActivatable):

	app = GObject.property(type=Gedit.App)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.app.set_accels_for_action("win.duplicate-line-up", ["<Super><Alt>Up"])
		self.app.set_accels_for_action("win.duplicate-line-down", ["<Super><Alt>Down"])

	def do_deactivate(self):
		self.app.set_accels_for_action("win.duplicate-line-up", [])
		self.app.set_accels_for_action("win.duplicate-line-down", [])


class DuplicateLineWindowActivatable(GObject.Object, Gedit.WindowActivatable):

	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		action = Gio.SimpleAction(name="duplicate-line-up")
		action.connect('activate', self.on_duplicate_line_up_activate)
		self.window.add_action(action)

		action = Gio.SimpleAction(name="duplicate-line-down")
		action.connect('activate', self.on_duplicate_line_down_activate)
		self.window.add_action(action)

	def do_deactivate(self):
		self.window.remove_action("duplicate-line-up")
		self.window.remove_action("duplicate-line-down")

	def do_update_state(self):
		self.window.lookup_action("duplicate-line-up").set_enabled(self.window.get_active_document() != None)
		self.window.lookup_action("duplicate-line-down").set_enabled(self.window.get_active_document() != None)

	def get_view_activatable(self, view):
		if not hasattr(view, "duplicate_line_view_activatable"):
			return None
		return view.duplicate_line_view_activatable

	def call_view_activatable(self, cb):
		view = self.window.get_active_view()

		if view:
			cb(self.get_view_activatable(view))

	# Menu activate handlers
	def on_duplicate_line_up_activate(self, action, parameter, user_data=None):
		self.call_view_activatable(lambda va: va.duplicate_line_up())

	def on_duplicate_line_down_activate(self, action, parameter, user_data=None):
		self.call_view_activatable(lambda va: va.duplicate_line_down())


class DuplicateLineViewActivatable(GObject.Object, Gedit.ViewActivatable):

	view = GObject.property(type=Gedit.View)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.view.duplicate_line_view_activatable = self

	def do_deactivate(self):
		delattr(self.view, "duplicate_line_view_activatable")

	def do_update_state(self):
		pass

	def duplicate_line_up(self):
		buf = self.view.get_buffer()
		insert = buf.get_insert()
		start = buf.get_iter_at_mark(insert)
		start.set_line_offset(0)
		end = start.copy()

		end.forward_line()
		text = buf.get_slice(start, end, True)
		if text is not None and text != "":
			forwarded = start.forward_line()

			buf.begin_user_action()
			if not forwarded:
				buf.insert(start, "\n")
			buf.insert(start, text)
			buf.end_user_action()

	def duplicate_line_down(self):
		buf = self.view.get_buffer()
		insert = buf.get_insert()
		start = buf.get_iter_at_mark(insert)
		start.set_line_offset(0)
		end = start.copy()

		end.forward_line()
		text = buf.get_slice(start, end, True)
		if text is not None and text != "":
			is_end = end.is_end()

			buf.begin_user_action()
			buf.insert(start, text)
			if is_end:
				buf.insert(start, "\n")
			buf.end_user_action()
