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
    layer = pdb.gimp_text_fontname(
        img, None, 0, 0, initstr, 10, True, size, PIXELS, font)
    # resize the img to the width and height of text layer
    img.resize(layer.width, layer.height, 0, 0)

    # finally display the image
    gimp.Display(img)


register(
    # this should be unique
    "python_fu_hello_world",
    # label?
    "Hello World image", "Create an image with user-passed string",
    # copyright?
    "Santosh Kumar", "Santosh Kumar", "2018",
    # what shall it be called in the menu?
    "Hello World",
    # if this is new image, leave it blank
    # see http://gimpbook.com/scripting/slides/pyreg-imgtype2.html
    "",
    # this is for GUI part
    [
        # (UI_ELEMENTS, "variable", "Label", Default)
        (PF_STRING, "string", "String", "Hello, World!"),
        (PF_FONT, "font", "Font face", "Sans"),
        (PF_SPINNER, "size", "Font size", 50, (1, 3000, 1)),
        (PF_COLOR, "color", "Text color", (1.0, 1.0, 1.0)),
    ],
    [],  # this is also blank, do you know why? edit this comment if you found
    # and where is the menu?
    hello_world, menu="<Image>/Filters/gimptosh"
)

main()
