import json
import random
from matplotlib.colors import to_rgb, to_hex
from colormath.color_objects import sRGBColor, HSVColor, LabColor, LCHuvColor, XYZColor, LCHabColor, AdobeRGBColor
from colormath.color_conversions import convert_color
import numpy as np
from xml.etree.ElementTree import parse, Element, SubElement, ElementTree
import xml.etree.ElementTree as ET
import os
import cv2
import torch
import matplotlib.pyplot as plt
from itertools import permutations

def color_picker(json_file, normalized=False):
    """
        Return normalized RGB tuples from colorhunt json file.
    """
    f = open(json_file)
    data = json.load(f)
    palettes = data["palettes"]
    num_palettes = len(palettes)
    palette_num = random.randint(0, num_palettes-1)
    
    colors = palettes[palette_num]["code"]
    rgb_list = []

    for i in range(0, len(colors), 6):
        if normalized:
            rgb_list.append(to_rgb("#"+colors[i:i+6]))
        else:
            r, g, b = to_rgb("#"+colors[i:i+6])
            rgb_list.append((int(r*255), int(g*255), int(b*255)))


    return rgb_list

def extend_colorhunt(normalized=False):

    f = open("colorhunt.json")
    data = json.load(f)
    palettes = data["palettes"]
    categories = data["categories"]
    num_palettes = len(palettes)

    with open('extended_colorhunt.json', 'r+') as ff:
        # {"code":"c8e4b29ed2be7eaa92ffd9b7","likes":726,"date":"2023-08-03T16:39:33.895Z","tags":"sage green teal peach pastel nature summer kids light food"}
        perms = list(permutations([0, 1, 2, 3], r=3))

        for j in range(num_palettes):
            for i in range(len(perms)):
                if i == 0:
                    continue
                else:
                    palette = palettes[j]["code"]
                    perm = perms[i]
                    rgb_list = []
                    for i in range(0, len(palette), 6):
                        r, g, b = to_rgb("#"+palette[i:i+6])
                        rgb_list.append((int(r*255), int(g*255), int(b*255)))
                    
                    new_palette = [rgb_list[perm[0]], rgb_list[perm[1]], rgb_list[perm[2]]]
                    hex_list = [to_hex(np.array(list(color))/255) for color in new_palette]
                    code = ""
                    for hex in hex_list:
                        code += hex[1:]
                    code = {"code":code,"likes":455,"date":"2023-08-10","tags":"none"}
                    palettes.append(code)
        
        new_data = {"categories": categories, "palettes":palettes}
        json.dump(new_data, ff)
                    
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

def bbox2VOC(filename, layer_name, bbox):
    bbox_smallest_x, bbox_smallest_y = bbox[0], bbox[1]
    bbox_biggest_x, bbox_biggest_y = bbox[2], bbox[3]
    width = bbox_biggest_x - bbox_smallest_x
    height = bbox_biggest_y - bbox_smallest_y
    return filename, width, height, layer_name, bbox_smallest_x, bbox_smallest_y, bbox_biggest_x, bbox_biggest_y

def create_xml(folder, filename, bbox_list):

    x = folder.split("/")
    bbox_list_voc = [bbox2VOC(filename, x[-1], bbox) for bbox in bbox_list]

    root = Element('annotation')
    SubElement(root, 'folder').text = folder
    SubElement(root, 'filename').text = filename
    SubElement(root, 'path').text = './images' +  filename
    source = SubElement(root, 'source')
    SubElement(source, 'database').text = 'Unknown'

    # Details from first entry
    e_filename, e_width, e_height, e_class_name, e_xmin, e_ymin, e_xmax, e_ymax = bbox_list_voc[0]
    
    size = SubElement(root, 'size')
    SubElement(size, 'width').text = str(e_width)
    SubElement(size, 'height').text = str(e_height)
    SubElement(size, 'depth').text = '3'

    SubElement(root, 'segmented').text = '0'

    for entry in bbox_list_voc:
        e_filename, e_width, e_height, e_class_name, e_xmin, e_ymin, e_xmax, e_ymax = entry
        
        obj = SubElement(root, 'object')
        SubElement(obj, 'name').text = e_class_name
        SubElement(obj, 'pose').text = 'Unspecified'
        SubElement(obj, 'truncated').text = '0'
        SubElement(obj, 'difficult').text = '0'

        bbox = SubElement(obj, 'bndbox')
        SubElement(bbox, 'xmin').text = str(e_xmin)
        SubElement(bbox, 'ymin').text = str(e_ymin)
        SubElement(bbox, 'xmax').text = str(e_xmax)
        SubElement(bbox, 'ymax').text = str(e_ymax)

    #indent(root)
    tree = ElementTree(root)
    
    xml_filename = os.path.join('.', folder, os.path.splitext(filename)[0] + '.xml')
    tree.write(xml_filename)

def VOC2bbox(xml_file: str):

    tree = ET.parse(xml_file)
    root = tree.getroot()

    list_with_all_boxes = []

    for boxes in root.iter('object'):

        filename = root.find('filename').text

        ymin, xmin, ymax, xmax = None, None, None, None

        ymin = int(float(boxes.find("bndbox/ymin").text))
        xmin = int(float(boxes.find("bndbox/xmin").text))
        ymax = int(float(boxes.find("bndbox/ymax").text))
        xmax = int(float(boxes.find("bndbox/xmax").text))

        if(xmax-xmin) == 0 or (ymax-ymin) == 0:
            continue
        else:
            list_with_single_boxes = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
            list_with_all_boxes.append(list_with_single_boxes)

    return filename, list_with_all_boxes

def test_bboxes(path):
    """
        Test whether annotations are correctly saved to xml files.
    """
    image = cv2.imread(path+"/00_preview/0000.png")
    _, text_bboxes = VOC2bbox(path+"/xmls/04_text/0000.xml")
    _, shape_bboxes = VOC2bbox(path+"/xmls/03_decoration/0000.xml")
    for box in text_bboxes:
        # [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
        xmin, ymin = np.min(box, axis=0)
        xmax, ymax = np.max(box, axis=0)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0,255,0), 2)

    for box in shape_bboxes:
        xmin, ymin = np.min(box, axis=0)
        xmax, ymax = np.max(box, axis=0)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0,255,0), 2)
    
    cv2.imwrite("result.jpg", image)

def check_distributions(colors=None):
    
    if colors == None:
        path = "../shape_dataset/processed_rgb_toy_dataset"
        colors = []
        for i in range(1000):
            data_path = path+"/data_{:04d}.pt".format(i)
            data = torch.load(data_path)
            for node in data.x:
                rgb = node[-3:]
                colors.append(rgb)

    n_bins = 20
    colors = np.array(colors)
    fig, axs = plt.subplots(1, 3, figsize=(30,10))
    plt.suptitle("Channel Distributions")
    N, bins, patches = axs[0].hist(colors[:, -3], bins=n_bins)
    axs[0].set_title("Red Channel")
    axs[0].set_xlabel("RGB Value")
    axs[0].set_ylabel("Count")
    N, bins, patches = axs[1].hist(colors[:, -2], bins=n_bins)
    axs[1].set_title("Green Channel")
    axs[1].set_xlabel("RGB Value")
    axs[1].set_ylabel("Count")
    N, bins, patches = axs[2].hist(colors[:, -1], bins=n_bins)
    axs[2].set_title("Blue Channel")
    axs[2].set_xlabel("RGB Value")
    axs[2].set_ylabel("Count")
    plt.show()
    plt.savefig("dist")
    plt.close()

if __name__ == "__main__":
    extend_colorhunt()