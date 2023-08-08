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
    canvas_size = 512
    included_shapes = ["circle", "square", "text"]
    shape_locations = ["random", "random", "title"]
    
    custom_position_dict = {
        "title": None,
        "top_left": None,
        "bottom_right": None,
        "middle": None,
    }

    # Color settings
    fixed_lightness_difference = 20