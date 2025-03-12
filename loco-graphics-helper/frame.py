'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

# Representation of a frame that is to be rendered


def recursive_hide_children(object, hide, type = 'NONE'):
    object.hide_render = hide
    for child in object.children:
        if child.loco_graphics_helper_object_properties.object_type != 'NONE':
            if type != 'NONE':
                continue
        recursive_hide_children(child, hide)

class Frame:
    def __init__(self, frame_index, task, view_angle, bank_angle=0, vertical_angle=0, mid_angle=0):
        self.frame_index = frame_index
        self.output_indices = [frame_index]
        self.task = task
        self.view_angle = view_angle
        self.bank_angle = bank_angle
        self.vertical_angle = vertical_angle
        self.mid_angle = mid_angle

        self.width = 1
        self.length = 1
        self.oversized = False
        self.invert_tile_positions = False

        self.recolorables = 0

        self.layer = "Editor"

        self.animation_frame_index = 0

        self.occlusion_layers = 0

        self.use_anti_aliasing = True
        self.anti_alias_with_background = False
        self.maintain_aliased_silhouette = True

        self.cast_shadows = True

        self.output_prefix = "Sprite"
        self.offset_x = 0
        self.offset_y = 0
        self.output_flags = 0
        self.output_zoomOffset = 0
        self.scale = (1, 1, 1)
        self.mirror_x = False
        self.view_angle_offset = -45

        self.base_palette = None

        self.target_object = None

    def get_meta_render_output_path(self, suffix=""):
        file_name = self.get_meta_render_output_file_name(suffix)
        if suffix != "":
            appended_frame_index = str(self.animation_frame_index).zfill(4)
            return os.path.join(self.task.get_temporary_output_folder(), "{}{}.exr".format(file_name, appended_frame_index))
        else:
            return os.path.join(self.task.get_temporary_output_folder(), "{}.mpc".format(file_name))

    def get_meta_render_output_file_name(self, suffix=""):
        if suffix != "":
            return "meta_render_{}_{}_".format(self.frame_index, suffix)
        else:
            return "meta_render_{}".format(self.frame_index)

    def get_base_render_output_path(self):
        return os.path.join(self.task.get_temporary_output_folder(), "render_{}.png".format(self.frame_index))

    def get_quantized_render_output_path(self):
        return os.path.join(self.task.get_temporary_output_folder(), "quantized_{}.png".format(self.frame_index))

    def get_final_output_paths(self):
        if self.oversized or self.occlusion_layers > 0:
            output_paths = []
            for output_index in self.output_indices:
                output_paths.append(os.path.join(
                    self.task.get_output_folder(), "sprites", "{}_{}.png".format(self.output_prefix, int(output_index))))
            return output_paths
        else:
            return [os.path.join(self.task.get_output_folder(), "sprites", "{}_{}.png".format(self.output_prefix,self.frame_index))]

    def prepare_scene_vehicle(self):
        location = None
        if not self.target_object is None:
            for o in bpy.data.scenes[0].objects:
                if o == self.target_object:
                    continue
                if o.loco_graphics_helper_object_properties.object_type == 'NONE':
                    continue
                recursive_hide_children(o,True)
            recursive_hide_children(self.target_object,False, self.target_object.loco_graphics_helper_object_properties.object_type)

            location = self.target_object.matrix_world.translation
            if self.target_object.loco_graphics_helper_vehicle_properties.bounding_box_override:
                location = self.target_object.loco_graphics_helper_vehicle_properties.bounding_box_override.matrix_world.translation
        # This is a little hacky...
        if self.layer == 'Top Down Shadow':
            bpy.data.objects['AirplaneShadowLight'].hide_render = False
        else:
            bpy.data.objects['AirplaneShadowLight'].hide_render = True
        return location

    def prepare_scene_track(self):
        for o in bpy.data.scenes[0].objects:
            if o.loco_graphics_helper_object_properties.object_type == 'NONE':
                continue
            recursive_hide_children(o,True)
        if self.target_object is not None:
            for o in self.target_object.objects:
                recursive_hide_children(o,False)
            return self.target_object.location
        return self.target_object.location

    def prepare_scene(self):
        object = bpy.data.objects['Rig']
        general_properties = bpy.context.scene.loco_graphics_helper_general_properties
        render_mode = general_properties.render_mode
        if object is None:
            return
        
        if render_mode == "VEHICLE":
            object.location = self.prepare_scene_vehicle()
        elif render_mode == "TRACK":
            object.location = self.prepare_scene_track()


        object.rotation_euler = (math.radians(self.bank_angle),
                                 math.radians(self.vertical_angle), math.radians(self.mid_angle))
        vJoint = object.children[0]
        vJoint.scale = self.scale
        vJoint.rotation_euler = (0, 0, math.radians(self.view_angle + self.view_angle_offset ))

    def set_anti_aliasing_with_background(self, use_anti_aliasing, anti_alias_with_background, maintain_aliased_silhouette):
        self.use_anti_aliasing = use_anti_aliasing

        # No need to anti-alias with background if anti-aliasing is disabled
        self.anti_alias_with_background = anti_alias_with_background and use_anti_aliasing

        # Always maintain aliased silhouttes when anti-aliasing with the background is disabled
        self.maintain_aliased_silhouette = ((
            not anti_alias_with_background) or maintain_aliased_silhouette) and use_anti_aliasing

    def set_offset(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y

    def set_offset_y(self, offset_y):
        self.offset_y = offset_y

    def set_multi_tile_size(self, width, length, invert_tile_positions):
        self.width = width
        self.length = length

        self.oversized = self.width > 1 or self.length > 1
        if self.oversized:
            self.invert_tile_positions = invert_tile_positions

    def set_layer(self, layer_name):
        self.layer = layer_name

    def set_recolorables(self, number_of_recolorables):
        self.recolorables = number_of_recolorables

    def set_base_palette(self, palette):
        self.base_palette = palette

    def set_occlusion_layers(self, layers):
        self.occlusion_layers = layers

    def set_output_indices(self, indices):
        self.output_indices = indices

        layers = self.occlusion_layers
        if layers == 0:
            layers = 1
        if len(self.output_indices) != self.width * self.length * layers:
            raise Exception(
                "The number of output indices does not match the number of expected output sprites for this frame")

    def oversize_order_scenery(self, start_output_index, number_of_viewing_angles, viewing_angle_index, animation_frames, animation_frame):
        output_indices = []
        for k in range(self.width * self.length):
            tile_index = k
            if self.invert_tile_positions:
                tile_index = (self.width * self.length - k - 1)
            output_indices.append(
                start_output_index + tile_index * animation_frames * number_of_viewing_angles + animation_frame * number_of_viewing_angles + viewing_angle_index)
        self.set_output_indices(output_indices)
        return self.width * self.length

    def oversize_order_track(self, start_output_index, number_of_viewing_angles, viewing_angle_index, animation_frames, animation_frame):
        if self.target_object is None:
            self.set_output_indices([start_output_index + viewing_angle_index * animation_frames * self.width * self.length + x for x in range(self.width * self.length)])
            return
        offset_order = self.target_object.manifest.get_output_order()
        num_sprites = len(self.target_object.manifest.subposition_order)
        output_indices = []
        for offset in offset_order:
            frame_number = offset + start_output_index
            frame_number += viewing_angle_index * num_sprites # do I bother with animation frames?
            output_indices.append(frame_number)
        self.set_output_indices(output_indices)
        return num_sprites

    def set_target_object(self, object):
        self.target_object = object

    def set_cast_shadows(self, cast_shadows):
        self.cast_shadows = cast_shadows

    def set_output_flags(self, flags):
        self.output_flags = flags

    def set_output_zoomOffset(self, offset):
        if offset < 0:
            raise Exception("Zoom Offset must be positive")
        if offset > self.frame_index:
            raise Exception("Zoom Offset may not be larger than the current sprite number")
        self.output_zoomOffset = offset
    
    def set_mirror_x(self, mirror):
        if mirror == self.mirror_x:
            return
        self.mirror_x = mirror
        if mirror:
            self.scale = (-1, 1, 1)
            self.view_angle_offset = -90-45
            self.view_angle = 360-self.view_angle
        else:
            self.scale = (1, 1, 1)
            self.view_angle_offset = -45
            self.view_angle = 360-self.view_angle
