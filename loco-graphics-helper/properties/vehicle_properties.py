'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from ..operators.render_operator import RCTRender


class SpriteTrackFlag(object):
    name = ""
    description = ""
    default_value = False
    section_id = None

    def __init__(self, section_id, name, description, default_value):
        self.section_id = section_id
        self.name = name
        self.description = description
        self.default_value = default_value


class VehicleProperties(bpy.types.PropertyGroup):
    sprite_track_flags_list = []

    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_FLAT",
        "Flat",
        "Render sprites for flat track",
        True))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES",
        "Gentle Slopes",
        "Render sprites for gentle sloped track",
        True))
    sprite_track_flags_list.append(SpriteTrackFlag(
        "VEHICLE_SPRITE_FLAG_STEEP_SLOPES",
        "Steep Slopes",
        "Render sprites for steep sloped track",
        False))

    defaults = []
    for sprite_track_flag in sprite_track_flags_list:
        defaults.append(sprite_track_flag.default_value)

    sprite_track_flags = bpy.props.BoolVectorProperty(
        name="Track Pieces",
        default=defaults,
        description="Which track pieces to render sprites for",
        size=len(sprite_track_flags_list))

    flat_viewing_angles = bpy.props.EnumProperty(
        name="Number of Flat Viewing Angles",
        items=(
            ("8", "8", "", 8),
            ("16", "16", "", 16),
            ("32", "32", "", 32),
            ("64", "64",
             "Default for most objects.", 64),
            ("128", "128", "", 128)
        ),
        default="64"
    )

    sloped_viewing_angles = bpy.props.EnumProperty(
        name="Number of Sloped Viewing Angles",
        items=(
            ("4", "4", "Default for road/tram vehicles", 4),
            ("8", "8", "", 8),
            ("16", "16", "", 16),
            ("32", "32", "Default for most trains", 32),
        ),
        default="32"
    )

    tilt_angle = bpy.props.FloatProperty(
        name="Tilt Angle",
        description="Renders a left and right tilting sprite at the specified angle if non-zero",
        default=0)

    index = bpy.props.IntProperty(
        name="Component Index",
        description="Car/sub-component's index",
        default=0,
        min=0,
        max=179)

    number_of_animation_frames = bpy.props.IntProperty(
        name="Animation Frames",
        description="Number of keyframed animation frames. Used for animated wheels and cargo",
        default=1,
        min=1)

    rotational_symmetry = bpy.props.BoolProperty(
        name="Rotational Symmetry",
        description="Component has 180-degree rotational symmetry. Reduces sprite count by half",
        default=False
    )

    braking_lights = bpy.props.BoolProperty(
        name="Has Braking Lights",
        description="Renders brake lights (layer 1)",
        default=False
    )

    is_airplane = bpy.props.BoolProperty(
        name="Is an airplane",
        description="Renders airplane shadows",
        default=False
    )

    is_clone = bpy.props.BoolProperty(
        name="Is a duplicate of another sub-component",
        description="Prevents rendering duplicate sprites for sub-components that are identical",
        default=False
    )

    is_inverted = bpy.props.BoolProperty(
        name="Component is reversed",
        description="The car draws this sub-component facing backwards",
        default=False
    )

    render_sprite = bpy.props.BoolProperty(
        name="Render component",
        description="Include this sub-component when batch rendering",
        default=True
    )

    null_component = bpy.props.BoolProperty(
        name="Null component",
        description="This sub-component is not rendered in the game",
        default=False
    )

    bounding_box_override = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="BBox override",
        description="Object to use when determining center of rotation and body parameters")

def register_vehicles_properties():
    bpy.types.Object.loco_graphics_helper_vehicle_properties = bpy.props.PointerProperty(
        type=VehicleProperties)


def unregister_vehicles_properties():
    del bpy.types.Object.loco_graphics_helper_vehicle_properties
