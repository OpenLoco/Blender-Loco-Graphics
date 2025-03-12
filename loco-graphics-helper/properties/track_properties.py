'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os
from ..builders.task_builder import TaskBuilder

from ..operators.render_operator import RCTRender

class TrackProperties(bpy.types.PropertyGroup):
    track_type = bpy.props.EnumProperty(
        name="Track Type",
        items=(
            ("RAIL", "Railway", "", 0),
            ("ROAD", "Road", "", 1),
            ("TRAM", "Tramway", "", 2),
        ),
        default="RAIL"
    )
    one_way = bpy.props.BoolProperty(
        name="one_way",
        description="Models for both directions required",
        default = False)


def register_track_properties():
    bpy.types.Scene.loco_graphics_helper_track_properties = bpy.props.PointerProperty(
        type=TrackProperties)


def unregister_track_properties():
    del bpy.types.Scene.loco_graphics_helper_track_properties
