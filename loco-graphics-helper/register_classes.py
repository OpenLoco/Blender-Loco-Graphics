'''
Copyright (c) 2026 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy

from .properties.preferences import RCTGraphicsHelperPreferences
from .properties.object_properties import register_object_properties, unregister_object_properties
from .properties.vehicle_properties import register_vehicles_properties, unregister_vehicles_properties
from .properties.tiles_properties import register_tiles_properties, unregister_tiles_properties
from .properties.walls_properties import register_walls_properties, unregister_walls_properties
from .properties.general_properties import register_general_properties, unregister_general_properties
from .properties.track_properties import register_track_properties, unregister_track_properties
from .rct_graphics_helper_panel import register_panel, unregister_panel
from .loco_object_helper_panel import register_object_panel, unregister_object_panel

from .operators.init_operator import Init
from .operators.render_tiles_operator import RenderTiles
from .operators.track_render_operator import RenderTrack
from .operators.vehicle_render_operator import RenderVehicle
from .operators.walls_render_operator import RenderWalls

from .builders.task_builder import TaskBuilder

def register_classes():
    register_general_properties()
    register_object_properties()
    register_tiles_properties()
    register_vehicles_properties()
    register_walls_properties()
    register_track_properties()
    register_panel()
    register_object_panel()

    bpy.utils.register_class(Init)
    bpy.utils.register_class(RenderTiles)
    bpy.utils.register_class(RenderTrack)
    bpy.utils.register_class(RenderVehicle)
    bpy.utils.register_class(RenderWalls)

def unregister_classes():
    unregister_general_properties()
    unregister_object_properties()
    unregister_tiles_properties()
    unregister_vehicles_properties()
    unregister_walls_properties()
    unregister_track_properties()
    unregister_panel()
    unregister_object_panel()

    bpy.utils.unregister_class(Init)
    bpy.utils.unregister_class(RenderTiles)
    bpy.utils.unregister_class(RenderTrack)
    bpy.utils.unregister_class(RenderVehicle)
    bpy.utils.unregister_class(RenderWalls)

