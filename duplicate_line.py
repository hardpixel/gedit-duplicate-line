import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gedit', '3.0')

from gi.repository import GObject, Gdk, Gtk, Gedit

class DuplicateLineWindowActivatable(GObject.Object, Gedit.WindowActivatable):

  window = GObject.property(type=Gedit.Window)

  def __init__(self):
    GObject.Object.__init__(self)

    self._handler_id = None

  def do_activate(self):
    self._handler_id = self.window.connect('key-press-event', self.on_key_press)

  def do_deactivate(self):
    self.window.disconnect(self._handler_id)

  def on_key_press(self, _key, event):
    if event.keyval in (Gdk.KEY_D, Gdk.KEY_d):
      modifiers = event.state & Gtk.accelerator_get_default_mod_mask()

      if modifiers == Gdk.ModifierType.CONTROL_MASK:
        self.duplicate_selection()
        return True

  def duplicate_selection(self):
    doc    = self.window.get_active_document()
    bounds = doc.get_selection_bounds()

    view   = self.window.get_active_view()
    buf    = view.get_buffer()
    insert = buf.get_insert()

    if len(bounds) == 0:
      start = buf.get_iter_at_mark(insert)
      start.set_line_offset(0)

      end = start.copy()
      end.forward_line()
    else:
      start, end = bounds

    text = buf.get_slice(start, end, True)

    if text is not None and text != '':
      is_end = end.is_end()
      buf.begin_user_action()
      buf.insert(start, text)

      if is_end:
        buf.insert(start, "\n")

      buf.end_user_action()
