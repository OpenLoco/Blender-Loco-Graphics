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
    bl_idname = "render.loco_vehicle"
    bl_label = "Render Loco Vehicle"

    def create_task(self, context):
        general_props = context.scene.loco_graphics_helper_general_properties

        self.task_builder.clear()
        self.task_builder.set_anti_aliasing_with_background(
            context.scene.render.use_antialiasing, general_props.anti_alias_with_background, general_props.maintain_aliased_silhouette)
        self.task_builder.set_output_index(general_props.out_start_index)
        self.task_builder.set_size(1, 1, False)

        # Add vehicle frames
        self.task_builder.set_recolorables(
            general_props.number_of_recolorables)
        self.task_builder.set_cast_shadows(
            general_props.cast_shadows)
        self.task_builder.set_palette(self.palette_manager.get_base_palette(
            general_props.palette, general_props.number_of_recolorables, "FULL"))

        bodies = [x for x in context.scene.objects if x.loco_graphics_helper_object_properties.object_type == "BODY" and not x.loco_graphics_helper_vehicle_properties.is_clone]
        bodies = sorted(bodies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)
        for body_object in bodies:
            self.add_render_angles(body_object)

        if bodies[0].loco_graphics_helper_vehicle_properties.is_airplane:
            self.task_builder.set_cast_shadows(
                True)
            self.task_builder.set_palette(self.palette_manager.get_shadow_palette())
            self.add_airplane_shadow_render_angles(bodies[0])
        else:
            bogies = [x for x in context.scene.objects if x.loco_graphics_helper_object_properties.object_type == "BOGIE" and not x.loco_graphics_helper_vehicle_properties.is_clone]
            bogies = sorted(bogies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)
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

    def add_render_angles(self, object):
        props = object.loco_graphics_helper_vehicle_properties
        is_bogie = object.loco_graphics_helper_object_properties.object_type == "BOGIE"
        target_object = object
        animation_frames = props.number_of_animation_frames
        roll_frames = 1 if props.roll_angle == 0 else 3
        
        for i in range(len(track_angle_sections_names)):
            key = track_angle_sections_names[i]
            if self.should_render_feature(key, props):
                track_sections = track_angle_sections[key]
                for track_section in track_sections:

                    base_view_angle = 0
                    self.task_builder.set_rotation(
                        base_view_angle, 0, vertical_angle=track_section[2])

                    num_viewing_angles = track_section[1]
                    if track_section[0] and is_bogie:
                        # Bogies have no transition sprites
                        continue

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

                    
                    if track_section[2] < 0 and props.is_airplane:
                        # We don't want to render anything so we are setting the target
                        # to the rig (could use anything though that can't render)
                        target_object = bpy.data.objects['Rig']
                    else:
                        target_object = object

                    for i in range(num_viewing_angles):
                        if roll_frames != 1:
                            roll_angles = [0, props.roll_angle, -props.roll_angle]
                            for j, roll_angle in enumerate(roll_angles):
                                frame_index = start_output_index + i * roll_frames + j
                                self.task_builder.set_rotation(
                                    base_view_angle, roll_angle, vertical_angle=track_section[2])
                                self.task_builder.add_frame(
                                    frame_index, num_viewing_angles, i, j, rotation_range, target_object)
                        else:
                            number_of_animated_and_other_frames = animation_frames + props.braking_lights
                            for j in range(animation_frames):
                                frame_index = start_output_index + i * number_of_animated_and_other_frames + j
                                self.task_builder.add_frame(
                                    frame_index, num_viewing_angles, i, j, rotation_range, target_object)

                            if props.braking_lights:
                                self.task_builder.set_layer("Braking Lights")
                                frame_index = start_output_index + i * number_of_animated_and_other_frames + animation_frames
                                self.task_builder.add_frame(
                                    frame_index, num_viewing_angles, i, 0, rotation_range, target_object)
                                self.task_builder.set_layer("Editor")

    def add_airplane_shadow_render_angles(self, object):
        props = object.loco_graphics_helper_vehicle_properties
        
        track_sections = track_angle_sections["VEHICLE_SPRITE_FLAG_FLAT"]
        for track_section in track_sections:

            base_view_angle = 0
            self.task_builder.set_rotation(
                base_view_angle, 0, vertical_angle=track_section[2])

            num_viewing_angles = int(int(props.flat_viewing_angles) / 2)

            rotational_symmetry = props.rotational_symmetry

            if rotational_symmetry:
                num_viewing_angles = int(num_viewing_angles / 2)

            rotation_range = 180 if rotational_symmetry else 360

            start_output_index = self.task_builder.output_index

            for i in range(num_viewing_angles):
                self.task_builder.set_layer("Top Down Shadow")
                frame_index = start_output_index + i
                self.task_builder.add_frame(
                    frame_index, num_viewing_angles, i, 0, rotation_range, object)
                self.task_builder.set_layer("Editor")
