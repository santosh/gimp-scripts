from gimpfu import *

def hello_world(initstr, font, size, color):
    if font == "Comic Sans MS":
        initstr = "Comic Sans? Really?"
    # 1, 1 is the initial size of Image
    # that will be expanded to text size later
    img = gimp.Image(1, 1, RGB)

    # forground color is set to color passed
    gimp.set_foreground(color)

    # img is the image we just created, we want to create text layer on that
    # initstr is the string we want to use
    # size will be the size of the font
    # font is the font we're going to use
    layer = pdb.gimp_text_fontname(img, None, 0, 0, initstr, 10, True, size, PIXELS, font)
    # resize the img to the width and height of text layer
    img.resize(layer.width, layer.height, 0, 0)

    # finally display the image
    gimp.Display(img)

hello_world("Hello, World!", "Comic Sans MS", 72, "#ffffff")
