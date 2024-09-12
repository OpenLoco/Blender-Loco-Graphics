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
from ..angle_sections.track import track_angle_sections, track_angle_sections_names


class RenderVehicle(RCTRender, bpy.types.Operator):
    bl_idname = "render.rct_vehicle"
    bl_label = "Render RCT Vehicle"

    def create_task(self, context):
        general_props = context.scene.rct_graphics_helper_general_properties

        self.task_builder.clear()
        self.task_builder.set_anti_aliasing_with_background(
            context.scene.render.use_antialiasing, general_props.anti_alias_with_background, general_props.maintain_aliased_silhouette)
        self.task_builder.set_output_index(general_props.out_start_index)
        self.task_builder.set_size(1, 1, False)

        # Add vehicle frames
        self.task_builder.set_recolorables(
            general_props.number_of_recolorables)
        self.task_builder.set_palette(self.palette_manager.get_base_palette(
            general_props.palette, general_props.number_of_recolorables, "FULL"))

        cars = [x for x in context.scene.objects if x.rct_graphics_helper_object_properties.object_type == "CAR"]
        cars = sorted(cars, key=lambda x: x.rct_graphics_helper_vehicle_properties.index)
        for car_object in cars:
            self.add_render_angles(car_object)

        bogies = [x for x in context.scene.objects if x.rct_graphics_helper_object_properties.object_type == "BOGIE"]
        bogies = sorted(bogies, key=lambda x: x.rct_graphics_helper_vehicle_properties.index)
        for bogie_object in bogies:
            self.add_render_angles(bogie_object)

        return self.task_builder.create_task(context)

    def key_is_property(self, key, props):
        for sprite_track_flagset in props.sprite_track_flags_list:
            if sprite_track_flagset.section_id == key:
                return True

    def property_value(self, key, props):
        i = 0
        for sprite_track_flagset in props.sprite_track_flags_list:
            if sprite_track_flagset.section_id == key:
                return props.sprite_track_flags[i]
            i += 1

    def should_render_feature(self, key, props):
        if self.key_is_property(key, props):
            if self.property_value(key, props):
                return True
        return False

    def add_render_angles(self, car_object):
        props = car_object.rct_graphics_helper_vehicle_properties
        animation_frames = props.number_of_animation_frames
        for i in range(len(track_angle_sections_names)):
            key = track_angle_sections_names[i]
            if self.should_render_feature(key, props):
                track_sections = track_angle_sections[key]
                for track_section in track_sections:

                    base_view_angle = 0
                    self.task_builder.set_rotation(
                        base_view_angle, 0, vertical_angle=track_section[2])

                    num_viewing_angles = track_section[1]
                    if not track_section[0]:
                        if i == 0:
                            num_viewing_angles = int(props.flat_viewing_angles)
                        else:
                            num_viewing_angles = int(props.sloped_viewing_angles)

                    rotational_symmetry = props.rotational_symmetry

                    if rotational_symmetry:
                        num_viewing_angles = int(num_viewing_angles / 2)

                    rotation_range = 180 if rotational_symmetry else 360

                    start_output_index = self.task_builder.output_index

                    for i in range(num_viewing_angles):
                        number_of_animated_and_other_frames = animation_frames + props.braking_lights

                        for j in range(animation_frames):
                            frame_index = start_output_index + i * number_of_animated_and_other_frames + j
                            self.task_builder.add_frame(
                                    frame_index, num_viewing_angles, i, j, rotation_range, car_object)

                        if props.braking_lights:
                            self.task_builder.set_layer("Braking Lights")
                            frame_index = start_output_index + i * number_of_animated_and_other_frames + animation_frames
                            self.task_builder.add_frame(
                                frame_index, num_viewing_angles, i, 0, rotation_range, car_object)
                            self.task_builder.set_layer("Editor")
