from gi.repository import GObject, Gio, Gdk, Gtk, Gedit

class DuplicateLineWindowActivatable(GObject.Object, Gedit.WindowActivatable):

	window = GObject.property(type=Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.handler_id = self.window.connect("key-press-event", self.on_key_press)

	def do_deactivate(self):
		self.window.disconnect(self.handler_id)

	def on_key_press(self, term, event):
		modifiers = event.state & Gtk.accelerator_get_default_mod_mask()

		if event.keyval in (Gdk.KEY_D, Gdk.KEY_d):
			if modifiers == Gdk.ModifierType.CONTROL_MASK:
				self.on_duplicate_line_key_press()
				return True

		return False

	def on_duplicate_line_key_press(self, action=None, user_data=None):
		doc = self.window.get_active_document()
		selection_iter = doc.get_selection_bounds()

		view = self.window.get_active_view()
		buf = view.get_buffer()
		insert = buf.get_insert()

		if len(selection_iter) == 0:
			start = buf.get_iter_at_mark(insert)
			start.set_line_offset(0)
			end = start.copy()
			end.forward_line()
		else:
			start = selection_iter[0]
			end = selection_iter[1]

		text = buf.get_slice(start, end, True)

		if text is not None and text != "":
			is_end = end.is_end()
			buf.begin_user_action()
			buf.insert(start, text)

			if is_end:
				buf.insert(start, "\n")

			buf.end_user_action()
