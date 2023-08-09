import json
import random
from matplotlib.colors import to_rgb
from colormath.color_objects import sRGBColor, HSVColor, LabColor, LCHuvColor, XYZColor, LCHabColor, AdobeRGBColor
from colormath.color_conversions import convert_color

def color_picker(normalized=False):
    """
        Return normalized RGB tuples from colorhunt json file.
    """
    f = open("colorhunt.json")
    data = json.load(f)
    palettes = data["palettes"]
    num_palettes = len(palettes)
    palette_num = random.randint(0, num_palettes)
    
    colors = palettes[palette_num]["code"]
    rgb_list = []
    for i in range(0,len(colors), 6):
        if normalized:
            rgb_list.append(to_rgb("#"+colors[i:i+6]))
        else:
            r, g, b = to_rgb("#"+colors[i:i+6])
            rgb_list.append((int(r*255), int(g*255), int(b*255)))
    return rgb_list

def RGB2CIELab(palette):
    obj_palette = []
    for color in [palette]:
        color = sRGBColor(*color, is_upscaled=True)
        color = list(convert_color(color, LabColor, through_rgb_type=AdobeRGBColor).get_value_tuple())
        obj_palette.append(color)
    return obj_palette

def CIELab2RGB(palette):
    obj_palette = []
    for color in palette:
        color = LabColor(*color)
        color = list(convert_color(color, sRGBColor, through_rgb_type=AdobeRGBColor).get_value_tuple())
        obj_palette.append(color)
    return obj_palette



