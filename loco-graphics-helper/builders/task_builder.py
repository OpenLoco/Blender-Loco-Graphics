'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from operator import length_hint
from ..frame import Frame
from ..render_task import RenderTask
from ..vehicle import get_vehicle_y_offset

# Builder for creating render tasks procedurally

def get_offset_y():
    properties = bpy.context.scene.loco_graphics_helper_general_properties
    if properties.render_mode == "TILES":
        return 0
    elif properties.render_mode == "VEHICLE":
        return get_vehicle_y_offset()
    elif properties.render_mode == "WALLS":
        return 0
    elif properties.render_mode == "TRACK":
        return 0

class TaskBuilder:

    # Builder class for creating render tasks
    def __init__(self):
        self.angles = []

        self.view_angle = 0
        self.bank_angle = 0
        self.vertical_angle = 0
        self.mid_angle = 0

        self.width = 1
        self.length = 1

        self.invert_tile_positions = False

        self.use_anti_aliasing = True
        self.anti_alias_with_background = False
        self.maintain_aliased_silhouette = True
        self.mirror_x = False

        self.target_object = None

        self.output_index = 0

        self.recolorables = 0

        self.cast_shadows = True

        self.layer = "Editor"

        self.palette = None

        self.offset_x = 0
        self.offset_y = 0
        self.output_flags = 0
        self.output_zoomOffset = 0

        self.output_prefix = "Sprite"
        self.occlusion_layers = 0

        self.task = RenderTask(None)

    def set_output_index(self, output_index):
        self.output_index = output_index

    def set_offset(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y

    def add_frame(self, frame_index, number_of_viewing_angles, angle_index, animation_index, rotation_range, target_object):
        angle = rotation_range / number_of_viewing_angles * angle_index

        frame = Frame(frame_index, self.task, angle + self.view_angle,
                        self.bank_angle, self.vertical_angle, self.mid_angle)
        frame.set_multi_tile_size(self.width, self.length, self.invert_tile_positions)

        frame.set_offset(self.offset_x, self.offset_y)

        frame.set_recolorables(self.recolorables)

        frame.set_cast_shadows(self.cast_shadows)

        frame.set_layer(self.layer)

        frame.set_base_palette(self.palette)

        frame.output_prefix = self.output_prefix
        frame.set_output_flags(self.output_flags)
        frame.set_output_zoomOffset(self.output_zoomOffset)
        frame.set_mirror_x(self.mirror_x)

        frame.set_anti_aliasing_with_background(
            self.use_anti_aliasing, self.anti_alias_with_background, self.maintain_aliased_silhouette)

        frame.animation_frame_index = animation_index

        frame.set_target_object(target_object)

        frame.set_offset_y(get_offset_y())

        self.angles.append(frame)
        self.output_index = self.output_index + 1

    def add_null_frames(self, number):
        self.output_index += number

    # Adds render angles for the given number of viewing angles relative to the currently configured rotation
    def add_viewing_angles(self, number_of_viewing_angles, animation_frame_index=0, animation_frames=1, rotational_symmetry=False, oversize_order = "SCENERY"):

        start_output_index = self.output_index

        if rotational_symmetry:
            number_of_viewing_angles = int(number_of_viewing_angles / 2)

        rotation_range = 180 if rotational_symmetry else 360
        frames = 0
        for viewing_angle_index in range(number_of_viewing_angles):
            for animation_frame in range(animation_frames):
                num_sprites = 1
                angle = rotation_range / number_of_viewing_angles * viewing_angle_index

                frame_index = start_output_index + viewing_angle_index * animation_frames + animation_frame
                frame = Frame(frame_index, self.task, angle + self.view_angle,
                              self.bank_angle, self.vertical_angle, self.mid_angle)
                frame.set_multi_tile_size(self.width, self.length, self.invert_tile_positions)

                frame.set_offset(self.offset_x, self.offset_y)

                frame.set_recolorables(self.recolorables)

                frame.set_cast_shadows(self.cast_shadows)

                frame.set_layer(self.layer)
                
                frame.set_target_object(self.target_object)

                frame.set_base_palette(self.palette)
                
                frame.output_prefix = self.output_prefix
                frame.set_output_flags(self.output_flags)
                frame.set_output_zoomOffset(self.output_zoomOffset)
                frame.set_mirror_x(self.mirror_x)

                frame.set_anti_aliasing_with_background(
                    self.use_anti_aliasing, self.anti_alias_with_background, self.maintain_aliased_silhouette)

                frame.animation_frame_index = animation_frame_index + animation_frame

                frame.set_occlusion_layers(self.occlusion_layers)

                frame.set_offset_y(get_offset_y())

                if self.occlusion_layers > 0:
                    output_indices = []
                    for k in range(self.occlusion_layers):
                        output_indices.append(
                            start_output_index + k * animation_frames * number_of_viewing_angles + animation_frame * number_of_viewing_angles + viewing_angle_index)
                    frame.set_output_indices(output_indices)
                    num_sprites = self.occlusion_layers

                if frame.oversized:
                    if oversize_order == "SCENERY":
                        num_sprites = frame.oversize_order_scenery(start_output_index, number_of_viewing_angles, viewing_angle_index, animation_frames, animation_frame)
                    elif oversize_order == "TRACK":
                        num_sprites = frame.oversize_order_track(start_output_index, number_of_viewing_angles, viewing_angle_index, animation_frames, animation_frame)
                    else:
                        raise Exception("Invalid oversize order type")
                frames += num_sprites
                self.angles.append(frame)
        """
        frames = number_of_viewing_angles * \
            animation_frames * self.width * self.length
        if self.occlusion_layers > 0:
            frames *= self.occlusion_layers
            """
        self.output_index += frames

    # Sets the number of recolorable materials
    def set_recolorables(self, number_of_recolorables):
        self.recolorables = number_of_recolorables

    # Sets the number of recolorable materials
    def set_cast_shadows(self, cast_shadows):
        self.cast_shadows = cast_shadows

    # Sets the base palette to use
    def set_palette(self, palette):
        self.palette = palette

    # Sets the layer to render
    def set_layer(self, layer_name):
        self.layer = layer_name

    # Sets the anti-aliasing parameters
    def set_anti_aliasing_with_background(self, use_anti_aliasing, anti_alias_with_background, maintain_aliased_silhouette):
        self.use_anti_aliasing = use_anti_aliasing

        # No need to anti-alias with background if anti-aliasing is disabled
        self.anti_alias_with_background = anti_alias_with_background and use_anti_aliasing

        # Always maintain aliased silhouttes when anti-aliasing with the background is disabled
        self.maintain_aliased_silhouette = ((
            not anti_alias_with_background) or maintain_aliased_silhouette) and use_anti_aliasing

    # Sets the size of the render in tiles
    def set_size(self, width, length, invert_tile_positions):
        self.width = width
        self.length = length
        self.invert_tile_positions = invert_tile_positions

    def set_mirror_scale(self, scale):
        self.scale = scale

    # Sets the rotation applied to future render angles
    def set_rotation(self, view_angle, bank_angle=0, vertical_angle=0, mid_angle=0):
        self.view_angle = view_angle
        self.bank_angle = bank_angle
        self.vertical_angle = vertical_angle
        self.mid_angle = mid_angle

    # Resets the rotation applied to future render angles
    def reset_rotation(self):
        self.view_angle = 0
        self.bank_angle = 0
        self.vertical_angle = 0
        self.mid_angle = 0
        self.mirror_x = False

    # Sets the number of occlusion layers
    def set_occlusion_layers(self, layers):
        self.occlusion_layers = layers

    # Creates a render task with the supplied angles. Clears the buffer for reuse of the task builder
    def create_task(self, context):
        task = self.task
        task.context = context
        task.frames = self.angles
        self.clear()
        return task

    def clear(self):
        self.angles = []

        self.width = 1
        self.length = 1
        self.output_flags = 0
        self.output_zoomOffset = 0

        self.set_offset(0, 0)
        self.target_object = None
        self.set_occlusion_layers(0)

        self.recolorables = 0

        self.task = RenderTask(None)

        self.reset_rotation()
        self.output_prefix = "Sprite"
        
