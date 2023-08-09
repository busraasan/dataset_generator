from config import GeneratorConfig
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from utils import *
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import colormath

config = GeneratorConfig()
colors = color_picker()
canvas_size = config.canvas_size
shape_count = config.shape_count
title = config.title
undertitle = config.undertitle
lightness_diff = config.fixed_lightness_difference

cielab_text = RGB2CIELab(colors[0])

if cielab_text[0][0] > 85:
    L = cielab_text[0][0]
    cielab_text = [[min(100, cielab_text[0][0] - lightness_diff//2), cielab_text[0][1], cielab_text[0][2]]]
    cielab_bg = [[min(100, L + lightness_diff//2), cielab_text[0][1], cielab_text[0][2]]]
else:
    cielab_bg = [[min(100, cielab_text[0][0] + lightness_diff), cielab_text[0][1], cielab_text[0][2]]]

rgb_bg = CIELab2RGB(cielab_bg)[0]
rgb_bg = (int(rgb_bg[0]*255), int(rgb_bg[1]*255), int(rgb_bg[2]*255))
rgb_text = CIELab2RGB(cielab_text)[0]
rgb_text = (int(rgb_text[0]*255), int(rgb_text[1]*255), int(rgb_text[2]*255))

image = Image.new("RGB", (canvas_size, canvas_size), color=rgb_bg)
draw = ImageDraw.Draw(image)

font_title = ImageFont.truetype("Arial.ttf", 32)
title_width, title_height = draw.textsize(title, font=font_title)
title_x = (canvas_size - title_width) // 2
title_y = (canvas_size - title_height) // 2 - 100

font_undertitle = ImageFont.truetype("Arial.ttf", 15)
text_width, text_height = draw.textsize(undertitle, font=font_undertitle)
undertitle_x = (canvas_size - text_width) // 2
undertitle_y = (canvas_size - text_height) // 2 - 50

for i, shape in enumerate(config.included_shapes):
    for j in range(0, shape_count[i]):

        coin = random.randint(0, 3)
        if coin == 0:
            rad = random.randint(30, 70)
            x = random.randint(0, 512-(rad+10))
            y = random.randint(0, title_y-(rad+10))
        else:
            rad = random.randint(30, 80)
            x = random.randint(0, 512-(rad+10))
            y = random.randint(title_y+title_height+text_height+50, 512-(rad+10))

        if shape == "circle":
            draw.ellipse((x, y, x+rad, y+rad), fill=colors[2])
        elif shape == "square":
            draw.rectangle((x, y, x+rad, y+rad), fill=colors[3])
        elif shape == "text":
            draw.text((title_x, title_y), title, fill=rgb_text, font=font_title)
            draw.text((undertitle_x, undertitle_y), undertitle, fill=rgb_text, font=font_undertitle)

image.save('sample-out.jpg')
