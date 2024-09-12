'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy

def object_type_update_func(self, context):
    object = context.object
    
    # Reset to fixed values for bogies
    if object.rct_graphics_helper_object_properties.object_type == "BOGIE":
        props = object.rct_graphics_helper_vehicle_properties
        props.flat_viewing_angles = "32"
        props.sloped_viewing_angles = "32"
        props.braking_lights = False
        props.number_of_animation_frames = 1

    # Reset to default for cars
    if object.rct_graphics_helper_object_properties.object_type == "CAR":
        props = object.rct_graphics_helper_vehicle_properties
        props.flat_viewing_angles = "64"
        props.sloped_viewing_angles = "32"


class ObjectProperties(bpy.types.PropertyGroup):
    object_type = bpy.props.EnumProperty(
        name="Object Type",
        items=(
            ("NONE", "None", "", 0),
            ("CAR", "Car", "", 1),
            ("BOGIE", "Bogie", "", 2),
            ("CARGO", "Cargo", "", 3),
        ),
        default="NONE",
        update=object_type_update_func
    )


def register_object_properties():
    bpy.types.Object.rct_graphics_helper_object_properties = bpy.props.PointerProperty(
        type=ObjectProperties)


def unregister_object_properties():
    del bpy.types.Object.rct_graphics_helper_object_properties
