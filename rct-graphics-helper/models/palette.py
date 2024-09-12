'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import subprocess
import os

from ..magick_command import MagickCommand
from ..res.res import res_path

palette_colors = [
    "black",
    "mutedOliveGreen",
    "mutedDarkYellow",
    "yellow",
    "mutedDarkRed",
    "mutedGrassGreen",
    "mutedAvocadoGreen",
    "green",
    "mutedOrange",
    "mutedPurple",
    "blue",
    "mutedSeaGreen",
    "purple",
    "red",
    "orange",
    "mutedDarkTeal",
    "pink",
    "brown",
    "amber",
    "gray",
    "brightYellow",
    "unusedHotPink",
    "recolor_1_loco",
    "transparent",
]


palette_colors_details = {
    "black": {
        "title": "Black",
        "Description": "Black to white tones",
        "default": True
    },
    "gray": {
        "title": "Gray",
        "Description": "4 extra gray tones",
        "default": True
    },
    "mutedOliveGreen": {
        "title": "Muted Olive Green",
        "Description": "Muted olive green",
        "default": True
    },
    "mutedDarkYellow": {
        "title": "Muted Dark Yellow",
        "Description": "Muted dark yellow",
        "default": True
    },
    "yellow": {
        "title": "Yellow",
        "Description": "Yellow",
        "default": True
    },
    "mutedDarkRed": {
        "title": "Muted Dark Red",
        "Description": "Muted dark red",
        "default": True
    },
    "mutedGrassGreen": {
        "title": "Muted Grass Green",
        "Description": "Muted grass green",
        "default": True
    },
    "mutedAvocadoGreen": {
        "title": "Muted Avocado Green",
        "Description": "Muted avocado green",
        "default": True
    },
    "green": {
        "title": "Green",
        "Description": "Green",
        "default": True
    },
    "mutedOrange": {
        "title": "Muted Orange",
        "Description": "Muted orange",
        "default": True
    },
    "mutedPurple": {
        "title": "Muted Purple",
        "Description": "Muted purple",
        "default": True
    },
    "blue": {
        "title": "Blue",
        "Description": "Blue",
        "default": True
    },
    "mutedSeaGreen": {
        "title": "Muted Sea Green",
        "Description": "Muted sea green",
        "default": True
    },
    "purple": {
        "title": "Purple",
        "Description": "Purple",
        "default": True
    },
    "red": {
        "title": "Red",
        "Description": "Red",
        "default": True
    },
    "orange": {
        "title": "Orange",
        "Description": "Orange",
        "default": True
    },
    "mutedDarkTeal": {
        "title": "Muted Dark Teal",
        "Description": "Muted dark teal",
        "default": True
    },
    "pink": {
        "title": "Pink",
        "Description": "Pink",
        "default": True
    },
    "brown": {
        "title": "Brown",
        "Description": "Brown",
        "default": True
    },
    "amber": {
        "title": "Amber",
        "Description": "Amber",
        "default": True
    },
    "brightYellow": {
        "title": "Bright Yellow",
        "Description": "4 extra yellow tones",
        "default": True
    },
    "unusedHotPink": {
        "title": "Unused Hot Pink",
        "Description": "Unused colour",
        "default": True
    },
    "transparent": {
        "title": "Transparent",
        "Description": "Transparent",
        "default": True
    },
    "recolor_1_loco": {
        "title": "Recolor 1 loco purple",
        "Description": "Purple used by OpenLoco to import recolor 1",
        "default": False
    }
}

palette_base_path = os.path.join(res_path, "palettes")
palette_groups_path = os.path.join(palette_base_path, "groups")

# Collection of color groups to create a palette from


class Palette:
    def __init__(self, path=None, colors=[]):
        self.colors = colors
        self.generated = False
        self.invalidated = False
        self.path = ""

        if path != None:
            self.path = path
            self.generated = True
            self.invalidated = True

    # Adds a list of colors to the palette
    def add_colors(self, colors):
        for color in colors:
            if not color in self.colors:
                self.invalidated = True
                self.colors.append(color)

    # Excludes a color from the palette
    def exclude_color(self, color):
        if color in self.colors:
            self.invalidated = True
            self.colors.remove(color)

    def clear(self):
        self.colors = []
        self.invalidated = True

    # Creates a copy of the palette
    def copy(self):
        copied_palette = Palette()
        copied_palette.colors = self.colors.copy()
        copied_palette.invalidated = self.invalidated
        copied_palette.generated = self.generated
        copied_palette.path = self.path
        return copied_palette

    # Prepares the palette for use by the render process. The palette image file is regenerated if necessary
    def prepare(self, renderer):
        if (not self.generated) or self.invalidated:
            self.generate_output(renderer, self.path)

    # Generates a palette image file
    def generate_output(self, renderer, output_path):
        cmd = MagickCommand("")

        color_paths = []
        for color in self.colors:
            color_paths.append(os.path.join(
                palette_groups_path, color + ".png"))

        cmd.as_montage(color_paths)

        subprocess.check_output(cmd.get_command_string(
            renderer.magick_path, output_path), shell=True)
        
        print(output_path)

        self.path = output_path
        self.generated = True
        self.invalidated = False
