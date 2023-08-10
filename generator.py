from config import GeneratorConfig
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from utils import *
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import os 

config = GeneratorConfig()
canvas_size = config.canvas_size
shape_count = config.shape_count
title = config.title
undertitle = config.undertitle
contrast_ratio = config.contrast_ratio
dataset_size = config.dataset_size
dataset_path = config.dataset_path

elements = ["preview", "background", "image", "text"]

img_path_dict = {
    'preview': dataset_path + '/00_preview/',
    'background': dataset_path + '/01_background/',
    'decoration': dataset_path + '/03_decoration/',
    'image': dataset_path + '/02_image/',
    'text': dataset_path + '/04_text/',
}

annotation_path_dict = {
    'preview': dataset_path + '/xmls' +'/00_preview/',
    'background': dataset_path + '/01_background/',
    'image': dataset_path + '/xmls' + '/02_image/',
    'decoration': dataset_path + '/xmls' + '/03_decoration/',
    'text': dataset_path + '/xmls' + '/04_text/',
}

if not os.path.exists(dataset_path + "/xmls"):
    os.mkdir(dataset_path + "/xmls")

for element in elements:
    if not os.path.exists(img_path_dict[element]):
        os.mkdir(img_path_dict[element])
    if not os.path.exists(annotation_path_dict[element]):
        os.mkdir(annotation_path_dict[element])

for k in range(dataset_size):

    # Initialize information fields to convert to xml files.
    all_bboxes = {
            'image':[], 
            'background':[], 
            'text':[]
    }
    all_images = {
        'image':[], 
        'background':[], 
        'text':[]
    }

    # Pick color and select lightness
    colors = color_picker()
    cielab_text = RGB2CIELab(colors[0])
    L = cielab_text[0][0]
    name = "{:04d}".format(k)

    # Adjust the contrast between text and background color using lightness in CIELab

    # try 50 - 50

    if L < 50:
        L_text = L
        L_bg = L + 50
    else:
        L_text = L - 50
        L_bg = L

    # if L > 80:
    #     L_text = L
    #     L_bg = L/contrast_ratio
    # elif L < 40:
    #     L_text = L
    #     L_bg = min(100, L*contrast_ratio)
    # else:
    #     coin = random.randint(0, 2)
    #     if coin == 0:
    #         L_text = min(100, L + contrast_ratio*10)
    #         L_bg = L_text/contrast_ratio
    #     else:
    #         L_bg = min(100, L + contrast_ratio*10)
    #         L_text = (L_bg)/contrast_ratio
            

    cielab_text = [[L_text, cielab_text[0][1], cielab_text[0][2]]]
    cielab_bg = [[L_bg, cielab_text[0][1], cielab_text[0][2]]]

    # Convert CIELab to RGB for both background and text
    rgb_bg = CIELab2RGB(cielab_bg)[0]
    rgb_bg = (int(rgb_bg[0]*255), int(rgb_bg[1]*255), int(rgb_bg[2]*255))
    rgb_text = CIELab2RGB(cielab_text)[0]
    rgb_text = (int(rgb_text[0]*255), int(rgb_text[1]*255), int(rgb_text[2]*255))

    # Set the background color and create an empty PIL Image to fill with shapes and text
    image = Image.new("RGB", (canvas_size, canvas_size), color=rgb_bg)
    # Save background image
    image.save(os.path.join(img_path_dict["background"], name+".png"))

    draw = ImageDraw.Draw(image)
    text_bboxes = []
    # Set settings for the fonts
    font_title = ImageFont.truetype("Arial.ttf", 32)
    title_width, title_height = draw.textsize(title, font=font_title)
    title_x = (canvas_size - title_width) // 2
    title_y = (canvas_size - title_height) // 2 - 100

    font_undertitle = ImageFont.truetype("Arial.ttf", 15)
    text_width, text_height = draw.textsize(undertitle, font=font_undertitle)
    undertitle_x = (canvas_size - text_width) // 2
    undertitle_y = (canvas_size - text_height) // 2 - 50
    
    text_bboxes.append([title_x-10, title_y-10, title_x+10+title_width, title_y+10+title_height])
    text_bboxes.append([undertitle_x-10, undertitle_y-10, undertitle_x+10+text_width, undertitle_y+10+text_height])
    create_xml(annotation_path_dict["text"], name +".xml", text_bboxes)

    # Generate shapes
    shape_bboxes = []
    for i, shape in enumerate(config.included_shapes):
        for j in range(0, shape_count[i]):
            # Shapes will be more located below the title and text. We also avoid overlapping shapes with the text.
            coin = random.randint(0, 3)
            if coin == 0:
                rad = random.randint(30, 70)
                x = random.randint(10, 512-(rad+10))
                y = random.randint(10, title_y-(rad+10))
            else:
                rad = random.randint(30, 80)
                x = random.randint(10, 512-(rad+10))
                y = random.randint(title_y+title_height+text_height+50, 512-(rad+10))

            if shape == "circle":
                draw.ellipse((x, y, x+rad, y+rad), fill=colors[2])
                bbox = [x-5, y-5, x+rad+5, y+rad+5]
                shape_bboxes.append(bbox)
            elif shape == "square":
                draw.rectangle((x, y, x+rad, y+rad), fill=colors[3])
                bbox = [x-5, y-5, x+rad+5, y+rad+5]
                shape_bboxes.append(bbox)
            elif shape == "text":
                draw.text((title_x, title_y), title, fill=rgb_text, font=font_title)
                draw.text((undertitle_x, undertitle_y), undertitle, fill=rgb_text, font=font_undertitle)

        create_xml(annotation_path_dict["decoration"], name +".xml", shape_bboxes)

    image.save(os.path.join(img_path_dict["preview"], name+".png"))
