#!/usr/bin/env python
# coding: utf-8
# vim:et:sta:sts=2:sw=2:ts=2:tw=0:
from __future__ import division, unicode_literals, print_function, absolute_import

import urwidm
import time
palette = [
    ('body', 'light gray', 'black'),
    ('header', 'white', 'dark blue'),
    ('footer', 'light green', 'black'),
    ('footer_key', 'yellow', 'black'),
    ('strong', 'white', 'black'),
    ('copyright', 'light blue', 'black'),
    ('authors', 'light cyan', 'black'),
    ('translators', 'light green', 'black'),
    ('focusable', 'light green', 'black'),
    ('unfocusable', 'dark blue', 'black'),
    ('focus', 'black', 'dark green'),
    ('focus_edit', 'yellow', 'black'),
    ('focus_icon', 'yellow', 'black'),
    ('focus_radio', 'yellow', 'black'),
    ('focus_combo', 'black', 'dark green'),
    ('comboitem', 'light gray', 'dark blue'),
    ('comboitem_focus', 'black', 'brown'),
    ('error', 'white', 'dark red'),
    ('focus_error', 'light red', 'black'),
    ('important', 'yellow', 'black', 'bold'),
    ('info', 'white', 'dark blue', 'bold'),
    ('error', 'white', 'dark red', 'bold'),
  ]
urwidm.set_i18n(ok="Accept")
ui = urwidm.raw_display.Screen()
ui.set_mouse_tracking()


def handleKeys(key):
  if not isinstance(key, tuple):  # only keyboard input
    key = key.lower()
    if key in ('q', 'f10'):
      raise urwidm.ExitMainLoop()


def focusGain(widget, context):
  print("\nFocus Gain on help {0} ({1})".format(context, widget))
  time.sleep(1)
  return True


def focusLost(widget, context):
  print("\nFocus Lost on help {0} ({1})".format(context, widget))
  time.sleep(1)
  return True


def connectFocus(widget, context):
  urwidm.connect_signal(widget, 'focusgain', focusGain, context)
  urwidm.connect_signal(widget, 'focuslost', focusLost, context)


def btn4_clicked(btn):
  dialog = urwidm.TextDialog(('info', "Button 4 clicked"), 10, 40, ('important', "Title here"))
  dialog.run(loop.screen, loop.widget)

header = urwidm.Text('Title')
footer = urwidm.Text('Q or F10 to quit')

btn1 = urwidm.ButtonMore('btn1')
# connectFocus(btn1, 'btn1')

btn2 = urwidm.ButtonMore('btn2')
# connectFocus(btn2, 'btn2')

edit = urwidm.EditMore('edit')
# connectFocus(edit, 'edit')

cb = urwidm.CheckBoxMore('checkbox')
# connectFocus(cb, 'checkbox')

radioGrp = []
radio1 = urwidm.RadioButtonMore(radioGrp, 'radio1')
# connectFocus(radio1, 'radio1')
radio2 = urwidm.RadioButtonMore(radioGrp, 'radio2')
# connectFocus(radio2, 'radio2')
cols = urwidm.ColumnsMore([radio1, radio2])
# connectFocus(cols, 'cols')

txt1 = urwidm.TextMore('text1')
btn3 = urwidm.ButtonMore('btn3')
# connectFocus(btn3, 'btn3')
btn4 = urwidm.ButtonMore('btn4', on_press=btn4_clicked)
# connectFocus(btn4, 'btn4')
gf = urwidm.GridFlowMore([txt1, btn3, btn4], 10, 2, 2, 'center')
# connectFocus(gf, 'gf')

btn5 = urwidm.ButtonMore('btn5')
# connectFocus(btn5, 'btn5')
cb = urwidm.ComboBox('combo', ['item1', 'item2'])
# connectFocus(cb, 'cb')
pile = urwidm.PileMore([btn5, cb], cb)
# connectFocus(pile, 'pile')
cols2 = urwidm.ColumnsMore([urwidm.TextMore('text2'), pile])
# connectFocus(cols2, 'cols2')

bodyList = [
    cols2,
    btn1,
    cols,
    btn2,
    gf,
  ]

body = urwidm.ListBoxMore(urwidm.SimpleListWalker(bodyList))
body.attr = 'body'
frame = urwidm.FrameMore(body, header, footer, focus_part='body')
frame.attr = 'body'
mainView = frame
loop = urwidm.MainLoop(mainView, palette, handle_mouse=True, unhandled_input=handleKeys, pop_ups=True)
loop.run()
