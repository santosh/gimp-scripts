#!/usr/bin/env python

# Draw arrows in GIMP, using the selection as a guide for where to draw.
#
# Copyright 2010 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL.


from gimpfu import *
import gtk
from gobject import timeout_add

# Direction "enums"
DIREC_N, DIREC_NE, DIREC_E, DIREC_SE, DIREC_S, DIREC_SW, DIREC_W, DIREC_NW \
    = range(8)

def python_fu_arrow_from_selection(img, layer, arrowangle, arrowsize,
                                   x1, y1, x2, y2) :
    """
    Draw an arrow from (x1, y1) to (x2, y2) with the head at (x2, y2).
    The size of the arrowhead is controlled by arrowsize, and the
    angle of it by arrowangle.
    """
    # Save the current selection:
    savesel = pdb.gimp_selection_save(img)
    pdb.gimp_selection_none(img)

    aangle = arrowangle * math.pi / 180.

    #
    # Draw the line first.
    # But don't go quite all the way to the end, because that
    # would make a rounded tip where the arrow point should be.
    #
    strokes = [ x1, y1, x2, y2 ]
    if x1 != x2 :
        xslop = int(arrowsize / 2)
        yslop = xslop * abs(float(y2 - y1) / float(x2 - x1))
    else :
        xslop = 0
        yslop = int(arrowsize / 2)
    if x1 < x2 : xslop = -xslop
    if y1 < y2 : yslop = -yslop
    strokes[2] += xslop
    strokes[3] += yslop

    #pdb.gimp_paintbrush_default(self.layer, 4, strokes)
    pdb.gimp_paintbrush(layer, 0, 4, strokes, 0, 0)

    #
    # Now make the arrowhead
    #
    theta = math.atan2(y2-y1, x2-x1)
    points = [ x2, y2,
               int(x2 - arrowsize * math.cos(theta - aangle)),
               int(y2 - arrowsize * math.sin(theta - aangle)),
               int(x2 - arrowsize * math.cos(theta + aangle)),
               int(y2 - arrowsize * math.sin(theta + aangle)) ]

    # Select the arrowhead shape
    pdb.gimp_free_select(img, 6, points, CHANNEL_OP_REPLACE,
                         True, False, 0)
    # Fill the arrowhead
    pdb.gimp_edit_fill(layer, FOREGROUND_FILL)
    # Restore the old selection
    pdb.gimp_selection_load(savesel)

def direc_to_coords(x1, y1, x2, y2, direction) :
    if direction == DIREC_N :
        return x1, y2, x1, y1
    elif direction == DIREC_NE :
        return x1, y2, x2, y1
    elif direction == DIREC_E :
        return x1, y1, x2, y1
    elif direction == DIREC_SE :
        return x1, y1, x2, y2
    elif direction == DIREC_S :
        return x1, y1, x1, y2
    elif direction == DIREC_SW :
        return x2, y1, x1, y2
    elif direction == DIREC_W :
        return x2, y1, x1, y1
    elif direction == DIREC_NW :
        return x2, y2, x1, y1
    
class ArrowWindow(gtk.Window):
    def __init__ (self, img, *args):
        self.img = img
        self.x1, self.y1, self.x2, self.y2 = 0, 0, 0, 0

        self.direction = DIREC_N
        self.changed = False
        self.arrowsize = 30
        self.arrowangle = 25

        # Make a new GIMP layer to draw on
        self.layer = gimp.Layer(img, "arrow", img.width, img.height,
                                RGBA_IMAGE, 100, NORMAL_MODE)
        img.add_layer(self.layer, 0)

        # Create the dialog
        win = gtk.Window.__init__(self, *args)

        # Obey the window manager quit signal:
        self.connect("destroy", gtk.main_quit)

        # Make the UI
        self.set_border_width(10)
        vbox = gtk.VBox(spacing=10, homogeneous=False)
        self.add(vbox)
        label = gtk.Label("Arrow Designer")
        vbox.add(label)
        label.show()

        table = gtk.Table(rows=2, columns=2, homogeneous=False)
        table.set_col_spacings(10)
        vbox.add(table)

        # Arrow size and sharpness
        label = gtk.Label("Arrowhead size (px)")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0)
        label.show()
        adj = gtk.Adjustment(self.arrowsize, 0, 200, 1)
        adj.connect("value_changed", self.arrowsize_cb)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        table.attach(scale, 1, 2, 0, 1)
        scale.show()

        label = gtk.Label("Arrowhead angle")
        label.set_alignment(xalign=0.0, yalign=1.0)
        table.attach(label, 0, 1, 1, 2, xoptions=gtk.FILL, yoptions=0)
        label.show()
        adj = gtk.Adjustment(self.arrowangle, 0, 80, 1)
        adj.connect("value_changed", self.arrowangle_cb)
        scale = gtk.HScale(adj)
        scale.set_digits(0)
        table.attach(scale, 1, 2, 1, 2)
        scale.show()

        table.show()

        # Selector for arrow direction
        hbox = gtk.HBox(spacing=5)

        btn = gtk.RadioButton(None, "N")
        btn.set_active(True)
        btn.connect("toggled", self.direction_cb, DIREC_N)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "NE")
        btn.connect("toggled", self.direction_cb, DIREC_NE)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "E")
        btn.connect("toggled", self.direction_cb, DIREC_E)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "SE")
        btn.connect("toggled", self.direction_cb, DIREC_SE)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "S")
        btn.connect("toggled", self.direction_cb, DIREC_S)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "SW")
        btn.connect("toggled", self.direction_cb, DIREC_SW)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "W")
        btn.connect("toggled", self.direction_cb, DIREC_W)
        hbox.add(btn)
        btn.show()
        btn = gtk.RadioButton(btn, "NW")
        btn.connect("toggled", self.direction_cb, DIREC_NW)
        hbox.add(btn)
        btn.show()

        vbox.add(hbox)
        hbox.show()

        # Make the dialog button box
        hbox = gtk.HBox(spacing=20)

        btn = gtk.Button("Close")
        hbox.add(btn)
        btn.show()
        btn.connect("clicked", gtk.main_quit)

        vbox.add(hbox)
        hbox.show()
        vbox.show()
        self.show()

        timeout_add(300, self.update, self)    
        return win

    def direction_cb(self, widget, data=None) :
        self.direction = data
        self.changed = True

    def arrowsize_cb(self, val) :
        self.arrowsize = val.value
        self.changed = True

    def arrowangle_cb(self, val) :
        self.arrowangle = val.value
        self.changed = True

    def arrow(self, x1, y1, x2, y2) :
        python_fu_arrow_from_selection(self.img, self.layer,
                                       self.arrowangle, self.arrowsize,
                                       x1, y1, x2, y2)

    def update(self, *args):
        exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds(self.img)
        timeout_add(500, self.update, self)
        if not exists :
            return   # No selection, no arrow
        if (self.x1, self.y1, self.x2, self.y2) == (x1, y1, x2, y2) \
                and not self.changed :
            return
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.changed = False

        # Clear the layer, erasing the old arrow
        self.layer.fill(TRANSPARENT_FILL)

        # Draw the new arrow.
        # Order is from, to: arrowhead goes on second X, Y pair.
        x1, y1, x2, y2 = direc_to_coords(x1, y1, x2, y2, self.direction)
        self.arrow(x1, y1, x2, y2)

        pdb.gimp_displays_flush()

def arrow_designer(image, layer) :
    r = ArrowWindow(image)
    gtk.main()

def arrow_from_selection(img, layer, angle, size, direction) :
    exists, x1, y1, x2, y2 = pdb.gimp_selection_bounds(img)
    if not exists :
        return

    x1, y1, x2, y2 = direc_to_coords(x1, y1, x2, y2, direction)

    python_fu_arrow_from_selection(img, layer, angle, size, x1, y1, x2, y2)

register(
         "python_fu_arrow_interactive",
         "Draw an arrow following the selection (interactive)",
         "Draw an arrow following the current selection, updating as the selection changes",
         "Akkana Peck", "Akkana Peck",
         "2010",
         "<Image>/Filters/Render/Arrow designer...",
         "*",
         [
         ],
         [],
         arrow_designer)

register(
         "python_fu_arrow_from_selection",
         "Draw an arrow following the current selection",
         "Draw an arrow following the current selection",
         "Akkana Peck", "Akkana Peck",
         "2010",
         "<Image>/Filters/Render/Arrow from selection...",
         "*",
         [
           (PF_SLIDER, "angle",  "Arrow angle", 30, (0, 200, 1)),
           (PF_SLIDER, "size",  "Arrow size", 25, (0, 80, 1)),
           (PF_OPTION, "direction", "Direction", 2,
            ("N", "NE", "E", "SE", "S", "SW", "W", "NW")),
         ],
         [],
         arrow_from_selection)

main()
