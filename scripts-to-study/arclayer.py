#!/usr/bin/env python

# arclayer.py: Gimp plug-in to warp one layer along an arc of a given radius.

# Copyright 2002 by Akkana Peck, http://www.shallowsky.com/software/
# You may use and distribute this plug-in under the terms of the GPL.

import math
import time
from gimpfu import *

def ClearRegion(pxlRgn, width, height) :
    # Try yet another way to clear the region:
    time1 = time.time()
    pxlRgn[0:width, 0:height] = "\x00\x00\x00\x00" * width * height
    print "Time to clear in one step:", time.time() - time1
    return

    time1 = time.time()
    clearPxl = "\x00\x00\x00\x00"
    for x in xrange(0, width) :
        # pxlRgn[x, 0:height] = "\x00" * height * 3
        for y in xrange(0, height) :
            pxlRgn[x, y] = clearPxl
    print "Time to iterate over the whole region:", time.time() - time1

    time1 = time.time()
    data = list(pxlRgn[0:width, 0:height])
    for x in xrange(1, len(data), 4) :
        data[x] = data[x + 2] = "\x00"
    pxlRgn[0:width, 0:height] = "".join(data)
    print "Time to clear Joao's way:", time.time() - time1

def python_arc_layer(img, layer, radius, ontop) :
    gimp.progress_init("Arcing layer" + layer.name + "...")

    # Spinner passes an integer, which will upset later calculations
    radius = float(radius)

    pdb.gimp_undo_push_group_start(img)

    layername = layer.name + " arc"
    # Calculate the size for the new layer
    theta2 = layer.width / radius / 2
    newWidth = int(2 * radius * math.sin(theta2))
    newHeight = int(layer.height * math.cos(theta2) 
            + .5 * radius * math.sin(theta2) * math.tan(theta2))
    #print "Old size: ",layer.width,"x",layer.height
    #print "New size: ",newWidth,"x",newHeight
    #print "r =", radius, ", theta/2 =", theta2

    # Create the new layer:
    destDrawable = gimp.Layer(img, layername, newWidth, newHeight,
                  layer.type, layer.opacity, layer.mode)
    img.add_layer(destDrawable, 0)
    xoff, yoff = layer.offsets
    destDrawable.translate(xoff - (newWidth - layer.width)/2,
                   yoff - (newHeight - layer.height)/2)

    # Try to clear the layer before drawing anything.
    # Unfortunately, this doesn't work.
    # pdb.gimp_rect_select(img, 0, 0, newWidth, newHeight, REPLACE, 0, 0)
    #pdb.gimp_selection_all(img)
    pdb.gimp_edit_clear(destDrawable)
    destDrawable.flush()

    srcRgn = layer.get_pixel_rgn(0, 0, layer.width, layer.height,
                     False, False)

    dstRgn = destDrawable.get_pixel_rgn(0, 0, newWidth, newHeight,
                        True, True)
    #ClearRegion(dstRgn, newWidth, newHeight)

    # Finally, loop over the region:                    
    for x in xrange(0, layer.width) :
        for y in xrange(0, layer.height) :
            # Calculate new coordinates
            phi = theta2 - x/radius
            if ontop :
                r = radius - y
                newy = int(radius - r * math.cos(phi))
                if (newy < 0) :
                    continue
            else :
                r = radius - layer.height + y
                newy = newHeight \
                       + int(r * math.cos(phi) - radius)
                if (newy > newHeight) :
                    continue
            newx = int(newWidth/2 - r * math.sin(phi))

            # dstRgn[newx, newy] = srcRgn[x, y]
            newval = srcRgn[x, y]
            dstRgn[newx, newy] = newval

            # Here is a fast cheat to fill in holes:
            # Write to one pixel above the new location.
            # If that's a valid location, then later
            # another set of coordinates will map to it,
            # and overwrite this value; if not, then it
            # would have been a hole, and this fills it.
            if (newy < newHeight-1) :
                dstRgn[newx, newy+1] = newval
            if (newx < newWidth-1) :
                dstRgn[newx+1, newy] = newval

        #print "Progress:", 100.0 * x / layer.width
        # Docs say progress_update takes a percent,
        # but it's really a fraction.
        gimp.progress_update(1.0 * x / layer.width)

    destDrawable.flush()
    destDrawable.merge_shadow(True)
    destDrawable.update(0, 0, newWidth,newHeight)

    # Remove the old layer
    img.remove_layer(layer)

    pdb.gimp_selection_none(img)
    pdb.gimp_undo_push_group_end(img)
    pdb.gimp_progress_end()
    pdb.gimp_displays_flush()

register(
           "python_fu_arc_layer",
    "Bend a layer in an arc",
    "Bend a layer in an arc",
    "Akkana Peck",
    "Akkana Peck",
    "2002",
    "<Image>/Filters/Distorts/ArcLayer(py)...",
    "RGBA",
    [
        (PF_SPINNER, "Radius", "Arc Radius (pixels)",
         400, (0, 2000, 50)),
        (PF_TOGGLE, "Top", "Top of circle?", 1),
    ],
    [],
    python_arc_layer)

main()
