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

    sprite_track_flags: bpy.props.BoolVectorProperty(
        name="Track Pieces",
        default=defaults,
        description="Which track pieces to render sprites for",
        size=len(sprite_track_flags_list))

    flat_viewing_angles: bpy.props.EnumProperty(
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

    sloped_viewing_angles: bpy.props.EnumProperty(
        name="Number of Sloped Viewing Angles",
        items=(
            ("4", "4", "Default for road/tram vehicles", 4),
            ("8", "8", "", 8),
            ("16", "16", "", 16),
            ("32", "32", "Default for most trains", 32),
        ),
        default="32"
    )

    roll_angle: bpy.props.IntProperty(
        name="Roll/Tilt Angle",
        description="Renders a left and right tilting sprite at the specified angle if non-zero",
        default=0,
        min=0) 

    index: bpy.props.IntProperty(
        name="Component Index",
        description="Car, Body, or Bogie index",
        default=0,
        min=0)

    number_of_animation_frames: bpy.props.IntProperty(
        name="Animation Frames",
        description="Number of keyframed animation frames. Used for animated wheels and cargo, or roll sprites if needed",
        default=1,
        min=1)

    rotational_symmetry: bpy.props.BoolProperty(
        name="Rotational Symmetry",
        description="Component has 180-degree rotational symmetry. Reduces sprite count by half",
        default=False
    )

    braking_lights: bpy.props.BoolProperty(
        name="Has Braking Lights",
        description="Renders brake lights (work-in-progress)",
        default=False
    )

    is_airplane: bpy.props.BoolProperty(
        name="Body is airplane",
        description="This body component stores the airplane shadows (work-in-progress)",
        default=False
    )

    is_clone: bpy.props.BoolProperty(
        name="Duplicate of another component",
        description="This component is identical to another component which is already being rendered",
        default=False
    )

    is_inverted: bpy.props.BoolProperty(
        name="Component is reversed",
        description="The component is drawn facing backwards when placed on the road/rails",
        default=False
    )

    render_sprite: bpy.props.BoolProperty(
        name="Render component",
        description="Include this component when batch rendering",
        default=True
    )

    null_component: bpy.props.BoolProperty(
        name="Null component",
        description="This component is not rendered in the game",
        default=False
    )

    bounding_box_override: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Boundbox Override",
        description="Object to use when determining center of rotation and body parameters")


def register_vehicles_properties():
    bpy.utils.register_class(VehicleProperties)
    bpy.types.Object.loco_graphics_helper_vehicle_properties = bpy.props.PointerProperty(
        type=VehicleProperties)


def unregister_vehicles_properties():
    bpy.utils.unregister_class(VehicleProperties)
    del bpy.types.Object.loco_graphics_helper_vehicle_properties
