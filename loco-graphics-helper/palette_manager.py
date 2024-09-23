'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import subprocess
import os
import bpy
import math

from .models.palette import Palette, palette_base_path

default_full_palette = Palette(os.path.join(
    palette_base_path, "base_loco_palette.png"), [
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
    "transparent"
])

recolor_1_loco_palette = Palette(os.path.join(
    palette_base_path, "recolor_1_loco_palette.bmp"), [
    "recolor_1_loco",
    "transparent"
])

recolor_2_palette = Palette(os.path.join(
    palette_base_path, "recolour_2_loco_palette.png"), [
    "pink",
    "transparent"
])

shadow_palette = Palette(os.path.join(
    palette_base_path, "shadow_palette.png"), [
    "shadowGrey", 
    "transparent"
])

custom_palette = Palette(os.path.join(
    palette_base_path, "custom_palette.bmp"), [
    "yellow",
])

# The palette manager takes care of the different palette modes and build a modified palette based on the selected parameters.


class PaletteManager:
    def __init__(self):
        self.recolor_palettes = [
            recolor_1_loco_palette,
            recolor_2_palette
        ]

    # Gets a base palette for the selected palette mode for the selected number of recolorables
    def get_base_palette(self, selected_palette_mode, recolors, preference="FULL"):
        if selected_palette_mode == "AUTO":
            selected_palette_mode = preference

        base_palette = None

        if selected_palette_mode == "FULL":
            base_palette = default_full_palette.copy()
            base_palette.invalidated = True
        elif selected_palette_mode == "CUSTOM":
            base_palette = custom_palette.copy()
            base_palette.invalidated = True
        else:
            raise Exception(
                "Failed to get base palette. Unknown palette mode " + selected_palette_mode + ".")

        for i in range(recolors):
            base_palette.exclude_color(self.recolor_palettes[i].colors[0])

        return base_palette

    # Gets the recolor palette for the specified recolor index
    def get_recolor_palette(self, recolor_index):
        return self.recolor_palettes[recolor_index]

    # Overwrites the colors of the custom palette
    def set_custom_palette(self, colors):
        custom_palette.clear()
        custom_palette.add_colors(colors)

    def get_shadow_palette(self):
        return shadow_palette
