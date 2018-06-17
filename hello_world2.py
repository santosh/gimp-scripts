from gimpfu import *

def hello_world(initstr, font, size, color):
    img = gimp.Image(1, 1, RGB)
    gimp.set_foreground(color)
    layer = pdb.gimp_text_fontname(img, None, 0, 0, initstr, 10, True, size, PIXELS, font)
    img.resize(layer.width, layer.height, 0, 0)

    gimp.Display(img)

hello_world("Hello, World!", "Arial", 72, "#ffffff")
