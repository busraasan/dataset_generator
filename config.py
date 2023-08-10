from dataclasses import dataclass

"""
    Rules to try: 
        * Add hue range for elements.
        * Fix positions and see whether it uses distance information from edges.
        * Complex rules from constrained-palette optimization paper
"""

@dataclass
class GeneratorConfig:
    """
        Rules:
            1 - Circles have the same color
            2 - Squares have the same color
            3 - Background and Text has a fixed distance between them
    """
    dataset_size = 3100 # remember that we have max 3100 color palettes
    dataset_path = "../shape_dataset_extended"
    canvas_size = 512
    included_shapes = ["circle", "square", "text"]
    shape_locations = ["random", "random", "title"]
    shape_count = [2, 3, 1]
    json_file = "extended_colorhunt.json"
    
    custom_position_dict = {
        "title": None,
        "top_left": None,
        "bottom_right": None,
        "middle": None,
    }

    # Color settings
    contrast_ratio = 3

    # Text settings
    title = "Lorem Ipsum Dolor"
    undertitle = "Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, \n consectetur, adipisci velit..."