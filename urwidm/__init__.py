#!/usr/bin/env python
# coding: utf-8
# vim:et:sta:sts=2:sw=2:ts=2:tw=0:
"""
More widgets for Urwid
Based on the work on curses_misc.py in Wicd.
"""
from __future__ import unicode_literals

__copyright__ = 'Copyright 2013-2014, Salix OS, 2008-2009 Andrew Psaltis'
__license__ = 'LGPL'
__version__ = '0.1.0'

from urwid import *
from urwid.signals import _signals as urwid_signals
from urwid.canvas import apply_text_layout as urwid_apply_text_layout
from urwid.util import is_mouse_press as urwid_is_mouse_press
from urwid.util import is_mouse_event as urwid_is_mouse_event
import gettext
import re
try:
  _
except NameError:
  gettext.install('')

class FocusEventWidget(Widget):
  signals = ['focusgain', 'focuslost'] # will be used by the metaclass of Widget to call register_signal
  _has_focus = False
  @property
  def has_focus(self):
    return self._has_focus
  def _can_gain_focus(self):
    return True
  def _can_loose_focus(self):
    return True
  def get_focused_subwidget(self):
    return None
  def _can_gain_focus_rec(self):
    ret = self._can_gain_focus()
    subw = self.get_focused_subwidget()
    if subw and isinstance(subw, FocusEventWidget):
      ret &= subw._can_gain_focus_rec()
    return ret
  def _can_loose_focus_rec(self):
    ret = self._can_loose_focus()
    subw = self.get_focused_subwidget()
    if subw and isinstance(subw, FocusEventWidget):
      ret &= subw._can_loose_focus_rec()
    return ret
  def _emit_focus_event(self, name, *args):
    """
    Return True if there is no callback, or if all callback answer True
    """
    result = True
    signal_obj = urwid_signals
    d = getattr(self, signal_obj._signal_attr, {})
    for callback, user_arg in d.get(name, []):
      args_copy = [self]
      args_copy.extend(args)
      if user_arg is not None:
        args_copy.append(user_arg)
      result &= bool(callback(*args_copy))
    return result
  def _emit_focusgain(self):
    """
    Return True if there is no callback, or if all callback answer True
    """
    return self._emit_focus_event('focusgain')
  def _emit_focuslost(self):
    """
    Return True if there is no callback, or if all callback answer True
    """
    return self._emit_focus_event('focuslost')
  def _emit_focusgain_rec(self):
    ret = self._emit_focusgain()
    subw = self.get_focused_subwidget()
    if subw and isinstance(subw, FocusEventWidget):
      ret &= subw._emit_focusgain_rec()
    return ret
  def _emit_focuslost_rec(self):
    ret = True
    subw = self.get_focused_subwidget()
    if subw and isinstance(subw, FocusEventWidget):
      ret = subw._emit_focuslost_rec()
    ret &= self._emit_focuslost()
    return ret
  def gain_focus(self):
    ret = self._can_gain_focus_rec()
    if ret:
      ret = self._emit_focusgain_rec()
    if ret:
      self._has_focus = True
    return ret
  def loose_focus(self):
    ret = self._can_loose_focus()
    if ret:
      ret = self._emit_focuslost_rec()
    if ret:
      self._has_focus = False
    return ret

class SensitiveWidgetBehavior(object):
  """
  Makes an object have mutable selectivity.
  """
  _default_sensitive_attr = ('focusable', 'focus')
  """
  sensitive_attr = tuple of (attr, focus_attr) when sensitive
      attr = attribute to apply to w
      focus_attr = attribute to apply when in focus, if None use attr
  """
  _default_unsensitive_attr = ('unfocusable', '')
  """
  unsensitive_attr = tuple of (attr, focus_attr) when not sensitive
      attr = attribute to apply to w
      focus_attr = attribute to apply when in focus, if None use attr
  """

  def __init__(self, state = True):
    if hasattr(self, '_sensitive'):
      return # already initialized
    self._sensitive = state
    self._sensitive_attr = self._default_sensitive_attr
    self._unsensitive_attr = self._default_unsensitive_attr
  def get_sensitive_attr(self):
    return self._sensitive_attr
  def set_sensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._sensitive_attr = attr
    self._invalidate()
  sensitive_attr = property(get_sensitive_attr, set_sensitive_attr)
  def get_unsensitive_attr(self):
    return self._unsensitive_attr
  def set_unsensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._unsensitive_attr = attr
    self._invalidate()
  unsensitive_attr = property(get_unsensitive_attr, set_unsensitive_attr)
  def get_attr(self):
    return (self.sensitive_attr, self.unsensitive_attr)
  def set_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self.set_sensitive_attr(attr)
    self.set_unsensitive_attr(attr)
  attr = property(get_attr, set_attr)
  def get_sensitive(self):
    return self._sensitive
  def set_sensitive(self, state):
    self._sensitive = state
    self._invalidate()
  sensitive = property(get_sensitive, set_sensitive)
  def selectable(self):
    return self._selectable and self.sensitive
  def canvas_with_attr(self, canvas, focus = False):
    """ Taken from AttrMap """
    new_canvas = CompositeCanvas(canvas)
    if self.sensitive:
      attr_tuple = self._sensitive_attr
    else:
      attr_tuple = self._unsensitive_attr
    if focus and attr_tuple[1]:
      attr_map = attr_tuple[1]
    else:
      attr_map = attr_tuple[0]
    if type(attr_map) != dict:
      attr_map = {None: attr_map}
    new_canvas.fill_attr_apply(attr_map)
    return new_canvas

class More(FocusEventWidget, SensitiveWidgetBehavior):
  """
  Class that combine a FocusEventWidget and a SensitiveWidgetBehavior.
  Parent of all other widgets defined here.
  """
  def __init__(self, sensitive = True):
    SensitiveWidgetBehavior.__init__(self, sensitive)
  def selectable(self):
    """
    Due to inheritance order, this will be the implementation of Widget,
    pulled from FocusEventWidget that will be used.
    So here we force to use the one from SensitiveWidgetBehavior
    """
    return SensitiveWidgetBehavior.selectable(self)

class TextMore(More, Text):
  _default_sensitive_attr = ('body', 'body')
  def __init__(self, markup, align = LEFT, wrap = SPACE, layout = None):
    More.__init__(self, False)
    Text.__init__(self, markup, align, wrap, layout)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class EditMore(More, Edit):
  _default_sensitive_attr = ('focusable', 'focus_edit')
  def __init__(self, caption = "", edit_text = "", multiline = False, align = LEFT, wrap = SPACE, allow_tab = False, edit_pos = None, layout = None, mask = None):
    More.__init__(self)
    self._selectable = True
    Edit.__init__(self, caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class IntEditMore(More, IntEdit):
  _default_sensitive_attr = ('focusable', 'focus_edit')
  def __init__(self, caption = "", default = None):
    More.__init__(self)
    self._selectable = True
    IntEdit.__init__(self, caption, default)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class SelectableIconMore(More, SelectableIcon):
  _default_sensitive_attr = ('focusable', 'focus_icon')
  def __init__(self, text, cursor_position = 1):
    More.__init__(self)
    self._selectable = True
    SelectableIcon.__init__(self, text, cursor_position)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class ButtonMore(More, Button):
  def __init__(self, label, on_press = None, user_data = None):
    More.__init__(self)
    self._selectable = True
    Button.__init__(self, label, on_press, user_data)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class CheckBoxMore(More, CheckBox):
  _default_sensitive_attr = ('focusable', 'focus_radio')
  states = {
    True: SelectableIconMore("[X]"),
    False: SelectableIconMore("[ ]"),
    'mixed': SelectableIconMore("[#]") }
  def __init__(self, label, state = False, has_mixed = False, on_state_change = None, user_data = None):
    More.__init__(self)
    self._selectable = True
    CheckBox.__init__(self, label, state, has_mixed, on_state_change, user_data)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class RadioButtonMore(More, RadioButton):
  _default_sensitive_attr = ('focusable', 'focus_radio')
  states = {
    True: SelectableIconMore("(X)"),
    False: SelectableIconMore("( )"),
    'mixed': SelectableIconMore("(#)") }
  def __init__(self, group, label, state = "first True", on_state_change = None, user_data = None):
    More.__init__(self)
    self._selectable = True
    RadioButton.__init__(self, group, label, state, on_state_change, user_data)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class WidgetWrapMore(More, WidgetWrap):
  def __init__(self, w):
    More.__init__(self)
    self._wrapped_widget = w
  def _render_with_attr(self, size, focus = False):
    canvas = self._w.render(size, focus = focus)
    return self.canvas_with_attr(CompositeCanvas(canvas), focus)
  def render(self, size, focus = False):
    return self._render_with_attr(size, focus)
  def selectable(self):
    return self._w.selectable() and self.sensitive
  def _can_gain_focus(self):
    if isinstance(self._w, FocusEventWidget):
      return self._w._can_gain_focus()
    else:
      return FocusEventWidget._can_gain_focus(self)
  def _can_loose_focus(self):
    if isinstance(self._w, FocusEventWidget):
      return self._w._can_loose_focus()
    else:
      return FocusEventWidget._can_loose_focus(self)
  def get_focused_subwidget(self):
    return self._w

class WidgetDecorationMore(More, WidgetDecoration):
  def __init__(self, original_widget):
    More.__init__(self)
    WidgetDecoration.__init__(self, original_widget)
  def _render_with_attr(self, size, focus = False):
    canvas = self._original_widget.render(size, focus = focus)
    return self.canvas_with_attr(CompositeCanvas(canvas), focus)
  def render(self, size, focus = False):
    return self._render_with_attr(size, focus)
  def selectable(self):
    return self._original_widget.selectable() and self.sensitive
  def _can_gain_focus(self):
    if isinstance(self._original_widget, FocusEventWidget):
      return self._original_widget._can_gain_focus()
    else:
      return FocusEventWidget._can_gain_focus(self)
  def _can_loose_focus(self):
    if isinstance(self._original_widget, FocusEventWidget):
      return self._original_widget._can_loose_focus()
    else:
      return FocusEventWidget._can_loose_focus(self)
  def get_focused_subwidget(self):
    return self._original_widget

class WidgetPlaceholderMore(WidgetDecorationMore, WidgetPlaceholder):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, original_widget):
    WidgetDecorationMore.__init__(self, original_widget)
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus = focus), focus)

class AttrMapMore(WidgetDecorationMore, AttrMap):
  def __init__(self, w, attr_map, focus_map = None):
    WidgetDecorationMore.__init__(self, w)
    AttrMap.__init__(self, w, attr_map, focus_map)
  def render(self, size, focus = False):
    return self.canvas_with_attr(AttrMap.render(self, size, focus), focus)

class AttrWrapMore(WidgetDecorationMore, AttrWrap):
  def __init__(self, w, attr, focus_attr = None):
    WidgetDecorationMore.__init__(self, w)
    AttrWrap.__init__(self, w, attr, focus_attr)
  def render(self, size, focus = False):
    return self.canvas_with_attr(AttrWrap.render(self, size, focus), focus)

class PaddingMore(WidgetDecorationMore, Padding):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, w, align = LEFT, width = PACK, min_width = None, left = 0, right = 0):
    WidgetDecorationMore.__init__(self, w)
    Padding.__init__(self, w, align, width, min_width, left, right)
  def render(self, size, focus = False):
    return self.canvas_with_attr(Padding.render(self, size, focus), focus)

class FillerMore(WidgetDecorationMore, Filler):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, body, valign = "middle", height = None, min_height = None):
    WidgetDecorationMore.__init__(self, body)
    Filler.__init__(self, body, valign, height, min_height)
  def render(self, size, focus = False):
    return self.canvas_with_attr(Filler.render(self, size, focus), focus)

class BoxAdapterMore(WidgetDecorationMore, BoxAdapter):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, box_widget, height):
    WidgetDecorationMore.__init__(self, box_widget)
    BoxAdapter.__init__(self, box_widget, height)
  def render(self, size, focus = False):
    return self.canvas_with_attr(BoxAdapter.render(self, size, focus), focus)

class WidgetContainerMore(More, WidgetContainer):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, widget_list):
    More.__init__(self)
    WidgetContainer.__init__(self, widget_list)

class FrameMore(More, Frame):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  _filler_widget_class = FillerMore
  def __init__(self, body, header = None, footer = None, focus_part = 'body'):
    More.__init__(self)
    self._selectable = True
    Frame.__init__(self, body, header, footer, focus_part)
    self.set_focus('body')
  def render(self, size, focus = False):
    """Render frame and return it."""
    (maxcol, maxrow) = size
    (htrim, ftrim),(hrows, frows) = self.frame_top_bottom((maxcol, maxrow), focus)
    combinelist = []
    depends_on = []
    head = None
    if htrim and htrim < hrows:
      head = self._filler_widget_class(self.header, 'top').render((maxcol, htrim), focus and self.focus_part == 'header')
    elif htrim:
      head = self.header.render((maxcol,), focus and self.focus_part == 'header')
      assert head.rows() == hrows, "rows, render mismatch"
    if head:
      combinelist.append((head, 'header', self.focus_part == 'header'))
      depends_on.append(self.header)
    if ftrim + htrim < maxrow:
      body = self.body.render((maxcol, maxrow - ftrim - htrim), focus and self.focus_part == 'body')
      combinelist.append((body, 'body', self.focus_part == 'body'))
      depends_on.append(self.body)
      pass
    foot = None
    if ftrim and ftrim < frows:
      foot = self._filler_widget_class(self.footer, 'bottom').render((maxcol, ftrim), focus and self.focus_part == 'footer')
    elif ftrim:
      foot = self.footer.render((maxcol,), focus and self.focus_part == 'footer')
      assert foot.rows() == frows, "rows, render mismatch"
    if foot:
      combinelist.append((foot, 'footer', self.focus_part == 'footer'))
      depends_on.append(self.footer)
    return self.canvas_with_attr(CanvasCombine(combinelist), focus)
    #return CanvasCombine(combinelist)
  def _get_focus_widget(self, part):
    assert part in ('header', 'footer', 'body')
    if part == 'header':
      focus_w = self.get_header()
    elif part == 'footer':
      focus_w = self.get_footer()
    else: # part == 'body'
      focus_w = self.get_body()
    return focus_w
  def set_focus(self, part):
    """
    Set the part of the frame that is in focus.
    part -- 'header', 'footer' or 'body'
    """
    assert part in ('header', 'footer', 'body')
    ok = True
    if self.has_focus:
      focus_w = self._get_focus_widget(self.get_focus())
      if focus_w and isinstance(focus_w, FocusEventWidget):
        ok = focus_w.loose_focus()
      if ok:
        focus_w = self._get_focus_widget(part)
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.gain_focus()
    if ok:
      Frame.set_focus(self, part)
  def get_focused_subwidget(self):
    return self._get_focus_widget(self.get_focus())

class PileMore(More, Pile):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, widget_list, focus_item = None):
    More.__init__(self)
    Pile.__init__(self, widget_list, focus_item)
  def selectable(self):
    return Pile.selectable(self) and self.sensitive
  def keypress(self, size, key):
    """
    Pass the keypress to the widget in focus.
    Unhandled 'up' and 'down' keys may cause a focus change.
    Copied from original Pile but with custom focus event handling.
    """
    item_rows = None
    if len(size) == 2:
      item_rows = self.get_item_rows(size, focus = True)
    i = self.widget_list.index(self.focus_item)
    f, height = self._get_item_types(i)
    if self.focus_item.selectable():
      tsize = self.get_item_size(size, i, True, item_rows)
      key = self.focus_item.keypress(tsize, key)
      if self._command_map[key] not in ('cursor up', 'cursor down'):
        return key
    if self._command_map[key] == 'cursor up':
      candidates = range(i - 1, -1, -1) # count backwards to 0
    else: # self._command_map[key] == 'cursor down'
      candidates = range(i + 1, len(self.widget_list))
    if not item_rows:
      item_rows = self.get_item_rows(size, focus = True)
    for j in candidates:
      if not self.widget_list[j].selectable():
        continue
      self._update_pref_col_from_focus(size)
      old_focus = self.focus_item
      self.set_focus(j)
      if old_focus == self.focus_item: # focus change has been denied
        return
      if not hasattr(self.focus_item,'move_cursor_to_coords'):
        return
      f, height = self._get_item_types(i)
      rows = item_rows[j]
      if self._command_map[key] == 'cursor up':
        rowlist = range(rows-1, -1, -1)
      else: # self._command_map[key] == 'cursor down'
        rowlist = range(rows)
      for row in rowlist:
        tsize=self.get_item_size(size,j,True,item_rows)
        if self.focus_item.move_cursor_to_coords(tsize, self.pref_col, row):
          break
      return
    # nothing to select
    return key
  def set_focus(self, item):
    """
    Set the item in focus.
    item -- widget or integer index
    """
    ok = True
    if not hasattr(self, "focus_item"):
      Pile.set_focus(self, item)
    if self.focus_item:
      focus_w = self.get_focus()
      if type(item) == int:
        new_focus_w = self.widget_list[item]
      else:
        new_focus_w = item
      if focus_w != new_focus_w:
        if focus_w and isinstance(focus_w, FocusEventWidget):
          ok = focus_w.loose_focus()
        if ok:
          if isinstance(new_focus_w, FocusEventWidget):
            ok = new_focus_w.gain_focus()
    if ok:
      Pile.set_focus(self, item)
  def get_focused_subwidget(self):
    return self.get_focus()
  def get_focus_pos(self):
    """
    Return the 1-based position of the select item in focus or 0 if none.
    """
    fw = self.get_focus()
    pos = 0
    if fw:
      pos = self.widget_list.index(fw)
    return pos
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus), focus)

class ColumnsMore(More, Columns):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, widget_list, dividechars = 0, focus_column = None, min_width = 1, box_columns = None):
    More.__init__(self)
    Columns.__init__(self, widget_list, dividechars, focus_column, min_width, box_columns)
  def selectable(self):
    return Columns.selectable(self) and self.sensitive
  def keypress(self, size, key):
    ret = None
    if self.focus_col is None:
      ret = key
    else:
      widths = self.column_widths(size)
      if self.focus_col < 0 or self.focus_col >= len(widths):
        ret = key
      else:
        i = self.focus_col
        mc = widths[i]
        w = self.widget_list[i]
        if self._command_map[key] not in ('cursor up', 'cursor down', 'cursor page up', 'cursor page down'):
          self.pref_col = None
        key = w.keypress((mc,) + size[1:], key)
        if self._command_map[key] not in ('cursor left', 'cursor right'):
          ret = key
        else:
          if self._command_map[key] == 'cursor left':
            candidates = range(i-1, -1, -1) # count backwards to 0
          else: # key == 'right'
            candidates = range(i+1, len(widths))
          for j in candidates:
            if not self.widget_list[j].selectable():
              continue
            self.set_focus_column(j)
            #ret = None
            ret = key
            break
          else:
            ret = key
    return ret
  def set_focus_column(self, num):
    """Set the column in focus by its index in self.widget_list."""
    ok = True
    if self.get_focus_column():
      focus_w = self.get_focus()
      if isinstance(focus_w, FocusEventWidget):
        ok = focus_w.loose_focus()
    if ok:
      focus_w = self.widget_list[num]
      if isinstance(focus_w, FocusEventWidget):
        ok = focus_w.gain_focus()
    if ok:
      Columns.set_focus_column(self, num)
  def set_focus(self, item):
    """Set the item in focus. item -- widget or integer index"""
    if type(item) == int:
      assert item>=0 and item<len(self.widget_list)
      position = item
    else:
      position = self.widget_list.index(item)
    ok = True
    if self.has_focus:
      if self.get_focus_column():
        focus_w = self.get_focus()
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.loose_focus()
      if ok:
        focus_w = self.widget_list[position]
        if isinstance(focus_w, FocusEventWidget):
          ok = focus_w.gain_focus()
    if ok:
      self.focus_col = position
      self._invalidate()
    return ok
  def get_focused_subwidget(self):
    return self.get_focus()
  def mouse_event(self, size, event, button, col, row, focus):
    """
    Send event to appropriate column.
    May change focus on button 1 press.
    """
    widths = self.column_widths(size)
    x = 0
    for i in range(len(widths)):
      if col < x:
        return False
      w = self.widget_list[i]
      end = x + widths[i]
      if col >= end:
        x = end + self.dividechars
        continue
      focus = focus and self.focus_col == i
      ok = True
      if urwid_is_mouse_press(event) and button == 1:
        if w.selectable():
          ok = self.set_focus(w)
      if not ok or not hasattr(w,'mouse_event'):
        return False
      return w.mouse_event((end-x,)+size[1:], event, button, col - x, row, focus)
    return False
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus), focus)

class GridFlowMore(More, GridFlow):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  _column_widget_class = ColumnsMore
  _padding_widget_class = PaddingMore
  _pile_widget_class = PileMore
  def __init__(self, cells, cell_width, h_sep, v_sep, align):
    More.__init__(self)
    GridFlow.__init__(self, cells, cell_width, h_sep, v_sep, align)
    for cell in cells:
      if cell.selectable():
        self.focus_cell = cell
        break
  def selectable(self):
    return GridFlow.selectable(self) and self.sensitive
  def generate_display_widget(self, size):
    """
    Actually generate display widget (ignoring cache)
    Copied from original GridFlow but with custom sub-widgets.
    """
    (maxcol,) = size
    d = Divider() # don't customize Divider, it's really a basic class.
    if len(self.cells) == 0: # how dull
      return d
    if self.v_sep > 1:
      # increase size of divider
      d.top = self.v_sep-1
    # cells per row
    bpr = (maxcol+self.h_sep) // (self.cell_width+self.h_sep)
    if bpr == 0: # too narrow, pile them on top of eachother
      l = [self.cells[0]]
      f = 0
      for b in self.cells[1:]:
        if b is self.focus_cell:
          f = len(l)
        if self.v_sep:
          l.append(d)
        l.append(b)
      return self._pile_widget_class(l, f)
    if bpr >= len(self.cells): # all fit on one row
      k = len(self.cells)
      f = self.cells.index(self.focus_cell)
      cols = self._column_widget_class(self.cells, self.h_sep, f)
      rwidth = (self.cell_width+self.h_sep)*k - self.h_sep
      row = self._padding_widget_class(cols, self.align, rwidth)
      return row
    out = []
    s = 0
    f = 0
    while s < len(self.cells):
      if out and self.v_sep:
        out.append(d)
      k = min(len(self.cells), s + bpr)
      cells = self.cells[s:k]
      if self.focus_cell in cells:
        f = len(out)
        fcol = cells.index(self.focus_cell)
        cols = self._column_widget_class(cells, self.h_sep, fcol)
      else:
        cols = self._column_widget_class(cells, self.h_sep)
      rwidth = (self.cell_width+self.h_sep)*(k-s)-self.h_sep
      row = self._padding_widget_class(cols, self.align, rwidth)
      out.append(row)
      s += bpr
    return self._pile_widget_class(out, f)
  def set_focus(self, cell):
    """
    Set the cell in focus.
    cell -- widget or integer index into self.cells
    """
    ok = True
    if self.has_focus:
      focus_w = self.get_focus()
      if type(cell) == int:
        focus_w_next = self.cells[cell]
      else:
        focus_w_next = cell
      if focus_w and focus_w != focus_w_next and isinstance(focus_w, FocusEventWidget):
        ok = focus_w.loose_focus()
        if ok and isinstance(focus_w_next, FocusEventWidget):
          ok = focus_w_next.gain_focus()
    if ok:
      GridFlow.set_focus(self, cell)
  def get_focused_subwidget(self):
    return self.get_focus()
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus), focus)

class OverlayMore(More, Overlay):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, top_w, bottom_w, align, width, valign, height, min_width = None, min_height = None):
    More.__init__(self)
    Overlay.__init__(self, top_w, bottom_w, align, width, valign, height, min_width, min_height)
  def selectable(self):
    return Overlay.selectable(self) and self.sensitive
  def get_focused_subwidget(self):
    return self.top_w
  def render(self, size, focus = False):
    return self.canvas_with_attr(self.__super.render(size, focus), focus)

class ListBoxMore(More, ListBox):
  _default_sensitive_attr = 'body'
  _default_unsensitive_attr = 'body'
  def __init__(self, body):
    More.__init__(self)
    self._selectable = True
    ListBox.__init__(self, body)
  def change_focus(self, size, position, offset_inset = 0, coming_from = None, cursor_coords = None, snap_rows = None):
    old_widget, old_focus_pos = self.body.get_focus()
    new_focus_pos = position
    # hack for found the current widget in the list walker.
    new_widget = self.body.get_next(new_focus_pos - 1)[0]
    ok = True
    if isinstance(old_widget, FocusEventWidget):
      ok = old_widget.loose_focus()
    if ok and isinstance(new_widget, FocusEventWidget):
      ok = new_widget.gain_focus()
    if ok:
      ListBox.change_focus(self, size, position, offset_inset, coming_from, cursor_coords, snap_rows)
    return ok
  def get_focused_subwidget(self):
    return self.get_focus()[0]
  def mouse_event(self, size, event, button, col, row, focus):
    """
    Pass the event to the contained widgets.
    May change focus on button 1 press.
    """
    (maxcol, maxrow) = size
    middle, top, bottom = self.calculate_visible((maxcol, maxrow), focus = True)
    if middle is None:
      return False
    _ignore, focus_widget, focus_pos, focus_rows, cursor = middle
    trim_top, fill_above = top
    _ignore, fill_below = bottom
    fill_above.reverse() # fill_above is in bottom-up order
    w_list = (fill_above + [(focus_widget, focus_pos, focus_rows)] + fill_below)
    wrow = -trim_top
    for w, w_pos, w_rows in w_list:
      if wrow + w_rows > row:
        break
      wrow += w_rows
    else:
      return False
    focus = focus and w == focus_widget
    ret = False
    if urwid_is_mouse_press(event) and button == 1:
      if w.selectable():
        ret = self.change_focus((maxcol, maxrow), w_pos, wrow)
      else:
        ret = True
    if ret and hasattr(w, 'mouse_event'):
      return w.mouse_event((maxcol,), event, button, col, row - wrow, focus)
    else:
      return False
  def render(self, size, focus = False):
    # hack to trigger a focus_gain on the first selectable widget
    if self.set_focus_pending == 'first selectable':
      for i, w in enumerate(self.body):
        if w.selectable():
          self.change_focus(size, i)
          break
    # render with attribute wrapping
    return self.canvas_with_attr(self.__super.render(size, focus), focus)

class LineBoxMore(WidgetDecorationMore, LineBox):
  def __init__(self, original_widget, title = "", tlcorner = '┌', tline = '─', lline = '│', trcorner = '┐', blcorner = '└', rline = '│', bline = '─', brcorner = '┘'):
    """See LineBox"""
    self._tline, self._bline = AttrMapMore(Divider(tline), None), AttrMapMore(Divider(bline), None)
    self._lline, self._rline = AttrMapMore(SolidFill(lline), None), AttrMapMore(SolidFill(rline), None)
    self._tlcorner, self._trcorner = TextMore(tlcorner), TextMore(trcorner)
    self._blcorner, self._brcorner = TextMore(blcorner), TextMore(brcorner)
    self.title_widget = TextMore(self.format_title(title))
    self.tline_widget = ColumnsMore([
      self._tline,
      ('flow', self.title_widget),
      self._tline,
    ])
    top = ColumnsMore([
      ('fixed', 1, self._tlcorner),
      self.tline_widget,
      ('fixed', 1, self._trcorner)
    ])
    middle = ColumnsMore([
      ('fixed', 1, self._lline),
      original_widget,
      ('fixed', 1, self._rline),
    ], box_columns = [0, 2], focus_column = 1)
    bottom = ColumnsMore([
      ('fixed', 1, self._blcorner), self._bline, ('fixed', 1, self._brcorner)
    ])
    pile = PileMore([('flow', top), middle, ('flow', bottom)], focus_item = 1)
    WidgetDecorationMore.__init__(self, original_widget)
    WidgetWrap.__init__(self, pile)
  def render(self, size, focus = False):
    for w in (self._tline, self._bline, self._lline, self._rline, self._tlcorner, self._trcorner, self._blcorner, self._brcorner, self.title_widget):
      if self.sensitive:
        w.attr = self.attr[0]
      else:
        w.attr = self.attr[1]
    return self.canvas_with_attr(LineBox.render(self, size, focus), focus)

class PopUpLauncherMore(WidgetDecorationMore, PopUpLauncher):
  def __init__(self, original_widget):
    WidgetDecorationMore.__init__(self, original_widget)
    self._pop_up_widget = None
  def render(self, size, focus = False):
    canv = WidgetDecorationMore.render(self, size, focus)
    if self._pop_up_widget:
      canv = CompositeCanvas(canv)
      canv.set_pop_up(self._pop_up_widget, **self.get_pop_up_parameters())
    return canv

class SelText(TextMore):
  """A selectable text widget. See Text and TextMore."""
  _default_sensitive_attr = ('focusable', 'focus_edit')
  def __init__(self, markup, align = LEFT, wrap = SPACE, layout = None):
    self.__super.__init__(markup, align, wrap, layout)
    self._selectable = True
    self.set_sensitive(True)
  def keypress(self, size, key):
    """Don't handle any keys."""
    return key

class ComboBox(PopUpLauncherMore):
  """A ComboBox of text objects"""
  class ComboSpace(WidgetWrapMore):
    """The actual menu-like space that comes down from the ComboBox"""
    signals = ['close', 'validate']
    def __init__(self, items, show_first = 0, item_attrs = ('comboitem', 'comboitem_focus')):
      """
      items     : stuff to include in the combobox
      show_first: index of the element in the list to pick first
      """
      normal_attr = item_attrs[0]
      focus_attr = item_attrs[1]
      sepLeft = AttrMapMore(SolidFill("│"), normal_attr)
      sepRight = AttrMapMore(SolidFill("│"), normal_attr)
      sepBottomLeft = AttrMapMore(Text("└"), normal_attr)
      sepBottomRight = AttrMapMore(Text("┘"), normal_attr)
      sepBottomCenter = AttrMapMore(Divider("─"), normal_attr)
      self._content = []
      for item in items:
        if isinstance(item, Widget):
          if item.selectable and hasattr(item, "text") and hasattr(item, "attr"): # duck typing
            self._content.append(item)
          else:
            raise ValueError, "items in ComboBox should be strings or selectable widget with a text and attr properties"
        else:
          self._content.append(SelText(item))
      self._listw = PileMore(self._content)
      if show_first is None:
        show_first = 0
      self.set_selected_pos(show_first)
      columns = ColumnsMore([
        ('fixed', 1, PileMore([BoxAdapter(sepLeft, len(items)), sepBottomLeft])),
        PileMore([self._listw, sepBottomCenter]),
        ('fixed', 1, PileMore([BoxAdapter(sepRight, len(items)), sepBottomRight])),
      ])
      filler = FillerMore(columns)
      self.__super.__init__(filler)
      self._selectable = True
      self._deco = [sepLeft, sepRight, sepBottomLeft, sepBottomRight, sepBottomCenter, self._listw]
      self.set_item_attrs(item_attrs)
    def get_size(self):
      maxw = 1
      maxh = 0
      for widget in self._content:
        w = 0
        h = 0
        for s in (None, ()):
          try:
            (w, h) = widget.pack(s)
          except:
            pass
        maxw = max(maxw, w + 1)
        maxh += h
      return (maxw + 2, maxh + 1)
    def set_item_attrs(self, item_attrs):
      for w in self._content:
        if hasattr(w, "attr"):
          w.attr = item_attrs
      w.attr = item_attrs
      for w in self._deco:
        w.attr = item_attrs
    def keypress(self, size, key):
      if key in 'esc':
        self.close()
      if key in ('enter', ' '):
        self.validate()
      else:
        return self.__super.keypress(size, key)
    def mouse_event(self, size, event, button, col, row, focus):
      ret = self.__super.mouse_event(size, event, button, col, row, focus)
      if urwid_is_mouse_press(event) and button == 1 and col > 1 and col < size[0] - 1 and row < size[1] - 1:
        self.validate()
      return ret
    def close(self):
      self.set_selected_pos(None)
      self._emit('close')
    def validate(self):
      self.set_selected_item(self._listw.get_focus())
      self._emit('validate')
    def get_selected_item(self):
      return self._selected_item
    def set_selected_item(self, item):
      try:
        pos = [i.text for i in self._content].index(item.text)
      except:
        pos = None
      self.set_selected_pos(pos)
    selected_item = property(get_selected_item, set_selected_item)
    def get_selected_pos(self):
      return self._selected_pos
    def set_selected_pos(self, pos):
      if pos is not None and pos < len(self._content):
        self._listw.set_focus(pos)
        self._selected_item = self._content[pos].text
        self._selected_pos = pos
      else:
        self._selected_item = None
        self._selected_pos = None
    selected_pos = property(get_selected_pos, set_selected_pos)

  _default_sensitive_attr = ('body', '')
  _default_unsensitive_attr = ('body', '')
  DOWN_ARROW = "↓"
  signals = ['displaycombo', 'change']

  def __init__(self, label = '', items = None, use_enter = True, focus_index = 0):
    """
    label       : bit of text that preceeds the combobox.  If it is "", then ignore it
    items       : stuff to include in the combobox
    use_enter   : does enter trigger the combo list
    focus_index : index of the element in the list to pick first
    """
    self.label = Text(label)
    if items is None:
      items = []
      focus_index = None
    self.cbox = self._create_cbox_widget()
    if label:
      w = ColumnsMore(
        [
          ('fixed', len(label), self.label),
          ('fixed', 1, self.cbox),
          ('fixed', len(self.DOWN_ARROW), Text(self.DOWN_ARROW))
        ], dividechars = 1)
    else:
      w = ColumnsMore(
        [
          ('fixed', 1, self.cbox),
          ('fixed', len(self.DOWN_ARROW), Text(self.DOWN_ARROW))
        ], dividechars = 1)
    self.__super.__init__(w)
    self.combo_attrs = ('comboitem', 'comboitem_focus')
    self.use_enter = use_enter
    self.set_list(items)
    self.set_selected_item(focus_index)
    self._overlay_left = 0
    self._overlay_width = len(self.DOWN_ARROW)
    self._overlay_height = len(items)
    connect_signal(self, 'displaycombo', self.displaycombo)
  def _create_cbox_widget(self):
    return SelText('')
  def _set_cbox_text(self, text):
    ok = False
    self.cbox._fromCombo = True # add a property to say that we set the text from the combo
    if not ok and hasattr(self.cbox, "set_text"):
      try:
        self.cbox.set_text(text)
        ok = True
      except:
        pass
    if not ok and hasattr(self.cbox, "set_edit_text"):
      try:
        self.cbox.set_edit_text(text)
        ok = True
      except:
        pass
    self.cbox._fromCombo = False
    if not ok:
      raise Exception, "Do not know how to set the text in the widget {0}".format(self.cbox)
  def _item_text(self, item):
    if isinstance(item, basestring):
      return item
    else:
      return item.text
  def get_selected_item(self):
    """ Return (text, index) or (text, None) if the selected text is not in the list """
    curr_text = self.cbox.text
    try:
      index = [self._item_text(i) for i in self.list].index(curr_text)
    except:
      index = None
    return (curr_text, index)
  def set_selected_item(self, index):
    """ Set widget focus. """
    if index is not None and isinstance(index, int):
      curr_text = self._item_text(self.list[index])
    elif index is not None and isinstance(index, basestring):
      curr_text = text
    else:
      curr_text = ''
    self._set_cbox_text(curr_text)
  selected_item = property(get_selected_item, set_selected_item)
  def get_sensitive(self):
    return self.cbox.get_sensitive()
  def set_sensitive(self, state):
    self.cbox.set_sensitive(state)
  def selectable(self):
    return self.cbox.selectable()
  def get_list(self):
    return self._list
  def set_list(self, items):
    self._list = items
    maxw = reduce(max, [len(self._item_text(item)) for item in self._list], 0) + 1
    zonepos = 0
    if self.label.text:
      zonepos = 1
    self._original_widget.column_types[zonepos] = ('fixed', maxw)
  list = property(get_list, set_list)
  def set_combo_attrs(self, normal_attr, focus_attr):
    self.combo_attrs = (normal_attr, focus_attr)
  def keypress(self, size, key):
    """
    If we press space or enter, be a combo box!
    """
    if key == ' ' or (self.use_enter and key == 'enter'):
      self._emit("displaycombo")
    else:
      return self._original_widget.keypress(size, key)
  def mouse_event(self, size, event, button, col, row, focus):
    maxcol = size[0]
    maxtxt = len(self.cbox.text) + 1
    if self.label.text:
      maxtxt += len(self.label.text) + 1
    if urwid_is_mouse_press(event) and button == 1 and col > maxtxt and col <= maxtxt + len(self.DOWN_ARROW):
      self._emit("displaycombo")
  def displaycombo(self, src):
    self.open_pop_up()
  def create_pop_up(self):
    index = self.selected_item[1]
    popup = self.ComboSpace(self.list, index, self.combo_attrs)
    self._overlay_left = 0
    if self.label.text:
      self._overlay_left = len(self.label.text)
    (self._overlay_width, self._overlay_height) = popup.get_size()
    connect_signal(popup, 'close', lambda x: self.close_pop_up())
    connect_signal(popup, 'validate', self.validate_pop_up)
    return popup
  def get_pop_up_parameters(self):
    return {'left':self._overlay_left, 'top':1, 'overlay_width':self._overlay_width, 'overlay_height':self._overlay_height}
  def validate_pop_up(self, popup):
    pos = self._pop_up_widget.selected_pos
    text = self._item_text(self.list[pos])
    self.close_pop_up()
    if self._emit_change_event(text, pos):
      self.set_selected_item(pos)
  def _emit_change_event(self, pos, text):
    """
    Return True if there is no callback, or if all callback answer True
    """
    result = True
    signal_obj = urwid_signals
    d = getattr(self, signal_obj._signal_attr, {})
    for callback, user_arg in d.get('change', []):
      args = (self, pos, text)
      result &= bool(callback(*args))
    return result

class ComboBoxEdit(ComboBox):
  """
  A ComboBox with an editable zone.
  The combo trigger on 'enter' only, disregarding the state for self.use_enter
  """
  def _create_cbox_widget(self):
    edit = EditMore(edit_text = '', wrap = CLIP)
    connect_signal(edit, 'change', self._on_edit_change)
    return edit
  def keypress(self, size, key):
    """
    If we press enter, be a combo box!
    """
    if key == 'enter': # discard state of self.use_enter
      self._emit("displaycombo")
    else:
      return self._original_widget.keypress(size, key)
  def _on_edit_change(self, edit, text):
    # prevent re-emit the change when this event has been triggered by the combo
    if hasattr(edit, '_fromCombo') and not edit._fromCombo:
      # we cannot prevent the edit widget from being modified, even if the combo event handlers says so
      # so just notify about the change
      self._emit_change_event(text, None)

class TextMultiValues(SelText):
  """
  A selectable text that render multiple separated values, but which only display one value
  """
  def __init__(self, texts, selPosition = 0, join = ' | ', align = LEFT, wrap = SPACE, layout = None):
    assert texts
    assert isinstance(texts, list)
    assert selPosition >= 0 and selPosition < len(texts)
    self._texts = texts
    self._selPosition = selPosition
    self._join = join
    self._fullText = join.join(texts)
    self.__super.__init__(texts[selPosition], align, wrap, layout)
  def set_text(self, markup):
    self.__super.set_text(markup)
    if hasattr(self, "texts"):
      self._texts[self._selPosition] = self._text
      self._updateTexts(True)
  def getTexts(self):
    return self._texts
  def setTexts(self, texts):
    self._texts = texts
    self._updateTexts(True)
  texts = property(getTexts, setTexts)
  def getSelPosition(self):
    return self._selPosition
  def setSelPosition(self, selPosition):
    self._selPosition = selPosition
    self._updateTexts(False)
  selPosition = property(getSelPosition, setSelPosition)
  def _updateTexts(self, doFull = True):
    if doFull:
      self._fullText = self._join.join(self._texts)
    self._text = self._texts[self._selPosition]
  def render(self, size, focus = False):
    (maxcol,) = size
    text = self._fullText
    attr = self.get_text()[1]
    trans = self.get_line_translation(maxcol, (text, attr))
    return self.canvas_with_attr(urwid_apply_text_layout(text, attr, trans, maxcol), focus)
  def _update_cache_translation(self, maxcol, ta):
    if ta:
      text, attr = ta
    else:
      text = self._fullText
      attr = self.get_text()[1]
      self._cache_maxcol = maxcol
      self._cache_translation = self._calc_line_translation(text, maxcol)
  def pack(self, size = None, focus = False):
    text = self._fullText
    attr = self.get_text()[1]
    if size is not None:
      (maxcol,) = size
      if not hasattr(self.layout, "pack"):
        return size
      trans = self.get_line_translation(maxcol, (text, attr))
      cols = self.layout.pack(maxcol, trans)
      return (cols, len(trans))
    i = 0
    cols = 0
    while i < len(text):
      j = text.find('\n', i)
      if j == -1:
        j = len(text)
      c = calc_width(text, i, j)
      if c > cols:
        cols = c
      i = j + 1
    return (cols, text.count('\n') + 1)



# This is a h4x3d copy of some of the code in Ian Ward's dialog.py example.
class DialogExit(Exception):
  """ Custom exception. """
  pass

class Dialog2(WidgetWrapMore):
  """ Base class for other dialogs. """
  def __init__(self, text, height, width, body = None):
    self.buttons = None
    self.width = int(width)
    if width <= 0:
      self.width = ('relative', 80)
    self.height = int(height)
    if height <= 0:
      self.height = ('relative', 80)
    self.body = body
    if body is None:
      # fill space with nothing
      body = FillerMore(Divider(), 'top')
    self.frame = FrameMore(body, focus_part = 'footer')
    if text is not None:
      self.frame.header = PileMore([
        Text(text, align='right'),
        Divider()
      ])
    w = AttrWrapMore(self.frame, 'body')
    self.__super.__init__(w)
  # buttons: tuple of name,exitcode
  def add_buttons(self, buttons):
    """ Add buttons. """
    l = []
    maxlen = 0
    for name, exitcode in buttons:
      b = ButtonMore(name, self.button_press)
      b.exitcode = exitcode
      b = AttrWrapMore(b, 'body', 'focus')
      l.append(b)
      maxlen = max(len(name), maxlen)
    maxlen += 4  # because of '< ... >'
    self.buttons = GridFlowMore(l, maxlen, 3, 1, 'center')
    self.frame.footer = PileMore([
      Divider(),
      self.buttons
    ], focus_item = 1)
  def button_press(self, button):
    """ Handle button press. """
    raise DialogExit(button.exitcode)
  def run(self, ui, parent):
    """ Run the UI. """
    ui.set_mouse_tracking()
    size = ui.get_cols_rows()
    overlay = OverlayMore(
      LineBoxMore(self._w),
      parent, 'center', self.width,
      'middle', self.height
    )
    try:
      while True:
        canvas = overlay.render(size, focus=True)
        ui.draw_screen(size, canvas)
        keys = None
        while not keys:
          keys = ui.get_input()
        for k in keys:
          if urwid_is_mouse_event(k):
            event, button, col, row = k
            overlay.mouse_event(size, event, button, col, row, focus = True)
          else:
            if k == 'window resize':
              size = ui.get_cols_rows()
            k = self._w.keypress(size, k)
            if k == 'esc':
              raise DialogExit(-1)
            if k:
              self.unhandled_key(size, k)
    except DialogExit, e:
      return self.on_exit(e.args[0])
  def on_exit(self, exitcode):
    """ Handle dialog exit. """
    return exitcode, ""
  def unhandled_key(self, size, key):
    """ Handle keypresses. """
    pass

class TextDialog(Dialog2):
  """ Simple dialog with text and "OK" button. """
  def __init__(self, text, height, width, header=None, align='left',
    buttons=(_('OK'), 1)):
    l = [Text(text)]
    body = ListBoxMore(SimpleListWalker(l))
    body = AttrWrapMore(body, 'body')
    Dialog2.__init__(self, header, height + 2, width + 2, body)
    if type(buttons) == list:
      self.add_buttons(buttons)
    else:
      self.add_buttons([buttons])
    self.frame.set_focus('footer')
  def unhandled_key(self, size, k):
    """ Handle keys. """
    if k in ('up', 'page up', 'down', 'page down'):
      self.frame.set_focus('body')
      self._w.keypress(size, k)
      self.frame.set_focus('footer')

class InputDialog(Dialog2):
  """ Simple dialog with text and entry. """
  def __init__(self, text, height, width, ok_name=_('OK'), edit_text=''):
    self.edit = EditMore(wrap='clip', edit_text=edit_text)
    body = ListBoxMore(SimpleListWalker([self.edit]))
    body = AttrWrapMore(body, 'editbx', 'editfc')
    Dialog2.__init__(self, text, height, width, body)
    self.frame.set_focus('body')
    self.add_buttons([(ok_name, 0), (_('Cancel'), -1)])
  def unhandled_key(self, size, k):
    """ Handle keys. """
    if k in ('up', 'page up'):
      self.frame.set_focus('body')
    if k in ('down', 'page down'):
      self.frame.set_focus('footer')
    if k == 'enter':
      # pass enter to the "ok" button
      self.frame.set_focus('footer')
      self._w.keypress(size, k)
  def on_exit(self, exitcode):
    """ Handle dialog exit. """
    return exitcode, self.edit.get_edit_text()

class OptCols(WidgetWrapMore):
  """ Htop-style menubar on the bottom of the screen. """
  class ClickCols(WidgetWrapMore):
    """ Clickable menubar. """
    def __init__(self, keyText, desc, attrKey, attrDesc, callback = None, keys = None):
      items = [('fixed', len(keyText) + 1, Text((attrKey, keyText))), Text((attrDesc, desc))]
      cols = ColumnsMore(items)
      cols.attr = attrDesc
      self.__super.__init__(cols)
      self.callback = callback
      self.keys = keys

    def mouse_event(self, size, event, button, x, y, focus):
      if event == "mouse press" and self.keys and len(self.keys):
        self.callback(self.keys[0]) # the first key is used
  # tuples = [((key1, key2, …), desc)], on_event gets passed a key
  # handler = function passed the key of the "button" pressed
  # attrs = (attr_key, attr_desc)
  # mentions of 'left' and right will be converted to <- and -> respectively
  def __init__(self, tuples, handler, attrs = ('body', 'infobar')):
    # Construct the texts
    textList = []
    # callbacks map the text contents to its assigned callback.
    self.callbacks = []
    for cmd in tuples:
      keys = cmd[0]
      if type(keys) != tuple:
        keys = (keys,)
      newKeys = {}
      for key in keys:
        newkey = reduce(lambda s, (f, t): s.replace(f, t), [
          ('ctrl ', 'Ctrl+'),
          ('meta ', 'Alt+'),
          ('left', '←'),
          ('right', '→'),
          ('up', '↑'),
          ('down', '↓'),
          ('page up', 'Page Up'),
          ('page down', 'Page Down'),
          ('esc', 'ESC'),
          ('enter', 'Enter')],
          key)
        if re.match(r"^[a-z]([0-9]*)$", newkey):
          newkey = newkey.upper()
        elif re.match(r".*\+.*", newkey):
          newkey = newkey.split("+")
          newkey = newkey[0] + "+" + newkey[1].upper()
        newKeys[key] = newkey
      desc = cmd[1]
      keyText = " / ".join([newKeys[key] for key in keys]) + ":"
      col = self.ClickCols(keyText, desc, attrs[0], attrs[1], handler, keys)
      textList.append(col)
    cols = ColumnsMore(textList)
    WidgetWrapMore.__init__(self, cols)

  def mouse_event(self, size, event, button, x, y, focus):
    """ Handle mouse events. """
    # Widgets are evenly long (as of current), so...
    return self._w.mouse_event(size, event, button, x, y, focus)
