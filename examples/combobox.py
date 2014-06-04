#!/usr/bin/python
# coding: utf-8
# vim:et:sta:sts=2:sw=2:ts=2:tw=0:
from __future__ import division, unicode_literals, print_function, absolute_import

import gettext
gettext.install('combobox')
import sys
sys.path.append('../lib/')
import urwidm


def pause():
  raw_input("pause")


class ComboBoxEditAdd(urwidm.ComboBoxEdit):
  def keypress(self, size, key):
    if key == '+':
      (item, pos) = self.get_selected_item()
      if pos is None:
        self.list.append(item)
    else:
      return self.__super.keypress(size, key)


def main_event(input):
  if input in ('q', 'Q', 'f10'):
    raise urwidm.ExitMainLoop

l1 = [
  "val1",
  "val2",
  "val3",
]


class ComplexWidget(urwidm.WidgetWrapMore):
  def __init__(self, left='', center='', right=''):
    w = urwidm.ColumnsMore([
      ('fixed', len(left), urwidm.Text(left)),
      ('fixed', len(center), urwidm.Text(center)),
      ('fixed', len(right), urwidm.Text(right))
    ])
    self.__super.__init__(w)

  def get_text(self):
    return self._w.widget_list[1].text.upper()

  def set_text(self, text):
    self._w.widget_list[1].set_text(text)
  text = property(get_text)

  def set_sensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._sensitive_attr = attr
    try:
      if hasattr(self._w, 'sensitive_attr'):
        self._w.sensitive_attr = attr
      for w in self._w.widget_list:
        if hasattr(w, 'sensitive_attr'):
          w.sensitive_attr = attr
    except:
      pass

  def set_unsensitive_attr(self, attr):
    if type(attr) != tuple:
      attr = (attr, attr)
    self._unsensitive_attr = attr
    try:
      if hasattr(self._w, 'unsensitive_attr'):
        self._.unsensitive_attr = attr
      for w in self._w.widget_list:
        if hasattr(w, 'unsensitive_attr'):
          w.unsensitive_attr = attr
    except:
      pass

  def keypress(self, size, key):
    return key

  def selectable(self):
    return True

  def pack(self, size=None, focus=False):
    if size is None:
      w = 0
      for sw in self._w.widget_list:
        w += len(sw.text)
      return (w, 1)
    else:
      self.__super.pack(size, focus)

l2 = [
  urwidm.SelText("prop1"),
  ComplexWidget("«left,", "prop2", ",right»"),
  urwidm.TextMultiValues(["text", "multi", "values"], selPosition=1),
]
fill = urwidm.Filler(urwidm.PileMore([
  urwidm.Padding(urwidm.Text("ComboBox tests"), 'center'),
  urwidm.Divider(),
  urwidm.Padding(urwidm.ComboBox(items=l1), 'center', 10),
  urwidm.Divider(),
  urwidm.Padding(urwidm.Text("Use + to add an item to the list"), 'center'),
  urwidm.Padding(ComboBoxEditAdd(label="props:", items=l2, focus_index=1), 'center', 20),
  urwidm.Divider(),
  urwidm.Padding(urwidm.Text("Q or F10 to quit"), 'center'),
]))
loop = urwidm.MainLoop(
    fill,
    [
      ('body', 'light gray', 'black'),
      ('header', 'dark blue', 'light gray'),
      ('footer', 'light green', 'black', 'bold'),
      ('footer_key', 'yellow', 'black', 'bold'),
      ('strong', 'white', 'black', 'bold'),
      ('focusable', 'light green', 'black'),
      ('unfocusable', 'brown', 'black'),
      ('focus', 'black', 'light green'),
      ('focus_edit', 'yellow', 'black'),
      ('focus_icon', 'yellow', 'black'),
      ('focus_radio', 'yellow', 'black'),
      ('comboitem', 'dark blue', 'dark cyan'),
      ('comboitem_focus', 'black', 'brown'),
      ('error', 'white', 'light red'),
      ('focus_error', 'light red', 'black'),
    ],
    pop_ups=True,
    unhandled_input=main_event)
loop.run()
