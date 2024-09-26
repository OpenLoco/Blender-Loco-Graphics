'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os
from mathutils import Vector

from .operators.init_operator import Init

from .operators.vehicle_render_operator import RenderVehicle

from .operators.walls_render_operator import RenderWalls

from .operators.track_render_operator import RenderTrack

from .operators.render_tiles_operator import RenderTiles

from .models.palette import palette_colors, palette_colors_details

class RepairConfirmOperator(bpy.types.Operator):
    """This action will clear out the default camera and light. Changes made to the rig object, compositor nodes and recolorable materials will be lost."""
    bl_idname = "loco_graphics_helper.repair_confirm"
    bl_label = "Do you want to (re)create the base scene?"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        bpy.ops.render.loco_init()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class GraphicsHelperPanel(bpy.types.Panel):
    bl_label = "Loco Graphics Helper"
    bl_idname = "VIEW3D_PT_loco_graphics_helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Loco Tools'

    def draw(self, context):

        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("loco_graphics_helper.repair_confirm", text="Initialize / Repair")

        if not "Rig" in context.scene.objects:
            return

        # General properties

        properties = scene.loco_graphics_helper_general_properties

        row = layout.row()
        row.separator()

        row = layout.row()
        row.label("General:")

        row = layout.row()
        row.prop(properties, "output_directory")

        row = layout.row()
        row.prop(properties, "out_start_index")

        row = layout.row()
        row.prop(properties, "y_offset")

        row = layout.row()
        row.prop(properties, "number_of_recolorables")

        if not properties.render_mode == "VEHICLE":
            row = layout.row()
            row.prop(properties, "number_of_animation_frames")

        row = layout.row()
        row.prop(properties, "cast_shadows")

        row = layout.row()
        row.prop(properties, "anti_alias_with_background")

        if properties.anti_alias_with_background:
            box = layout.box()
            row = box.row()
            row.prop(properties, "maintain_aliased_silhouette")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.label("Dither Palette:")

        row = layout.row()
        row.prop(properties, "palette", text="")

        if properties.palette == "CUSTOM":
            box = layout.box()
            split = box.split(.50)
            columns = [split.column(), split.column()]
            i = 0
            for color in palette_colors:
                details = palette_colors_details[color]
                columns[i % 2].row().prop(properties, "custom_palette_colors",
                                          index=i, text=details["title"])
                i += 1

        row = layout.row()
        row.label("Object Type:")

        row = layout.row()
        row.prop(properties, "render_mode", text="")

        box = layout.box()

        # Specialized properties

        if properties.render_mode == "TILES":
            self.draw_tiles_panel(scene, box)
        elif properties.render_mode == "VEHICLE":
            self.draw_vehicle_panel(scene, box)
        elif properties.render_mode == "WALLS":
            self.draw_walls_panel(scene, box)
        elif properties.render_mode == "TRACK":
            self.draw_track_panel(scene, box)

        row = layout.row()
        row.prop(properties, "build_gx")

        if properties.build_gx:
            box = layout.box()
            box.prop(properties, "build_assetpack")

            if properties.build_assetpack:
                box2 = box.box()
                box2.prop(properties, "copy_assetpack_to_orct2")

        row = layout.row()
        row.prop(properties, "build_parkobj")

        if properties.build_parkobj:
            box = layout.box()
            box.prop(properties, "copy_parkobj_to_orct2")

    def draw_tiles_panel(self, scene, layout):
        properties = scene.loco_graphics_helper_static_properties
        general_properties = scene.loco_graphics_helper_general_properties

        row = layout.row()
        row.prop(properties, "viewing_angles")

        row = layout.row()
        row.prop(properties, "object_width")
        row.prop(properties, "object_length")

        row = layout.row()
        if properties.object_width > 1 or properties.object_length > 1:
            row.prop(properties, "invert_tile_positions")

        row = layout.row()
        text = "Render"
        if general_properties.rendering:
            text = "Failed"
        row.operator("render.loco_static", text=text)

    def draw_walls_panel(self, scene, layout):
        properties = scene.loco_graphics_helper_walls_properties
        general_properties = scene.loco_graphics_helper_general_properties

        row = layout.row()
        row.prop(properties, "sloped")

        row = layout.row()
        row.prop(properties, "double_sided")

        row = layout.row()
        row.prop(properties, "doorway")

        row = layout.row()
        text = "Render"
        if general_properties.rendering:
            text = "Failed"
        row.operator("render.loco_walls", text=text)

    def draw_track_panel(self, scene, layout):
        properties = scene.loco_graphics_helper_track_properties
        general_properties = scene.loco_graphics_helper_general_properties

        row = layout.row()
        row.label("Work in progress")
        
        #row = layout.row()
        #row.operator("render.loco_track", text="Generate Splines")
        #
        #row = layout.row()
        #row.prop(properties, "placeholder")
#
        #if "Rig" in context.scene.objects:
        #    row = layout.row()
        #    text = "Render"
        #    if general_properties.rendering:
        #        text = "Failed"
        #    row.operator("render.loco_track", text=text)
    @staticmethod
    def get_number_of_sprites(object):
        is_bogie = object.loco_graphics_helper_object_properties.object_type == "BOGIE"
        props = object.loco_graphics_helper_vehicle_properties

        multiplier = props.number_of_animation_frames
        if props.roll_angle != 0:
            multiplier = 3
        elif props.braking_lights:
            multiplier = multiplier + 1
        if props.rotational_symmetry:
            multiplier = multiplier / 2

        num_transition_sprites = 0 if is_bogie else 4 + 4
        num_sprites = 0
        if props.sprite_track_flags[0]:
            num_sprites = int(props.flat_viewing_angles) * multiplier
        if props.sprite_track_flags[1]:
            num_sprites = num_sprites + (int(props.sloped_viewing_angles) * 2 + num_transition_sprites) * multiplier
        if props.sprite_track_flags[2]:
            num_sprites = num_sprites + (int(props.sloped_viewing_angles) * 2 + num_transition_sprites) * multiplier
        
        if props.is_airplane:
            num_sprites = num_sprites + int(props.flat_viewing_angles) * multiplier / 2
        return int(num_sprites)

    @staticmethod
    def get_min_max_x_bound_box_corners(object):
        bbox_corners = [object.matrix_world * Vector(corner) for corner in object.bound_box]
        min_x = min([x[0] for x in bbox_corners])
        max_x = max([x[0] for x in bbox_corners])
        return (min_x, max_x)

    @staticmethod
    def get_longest_component_edge(front, back, body):
        mins = []
        maxs = []
        if not front is None:
            min_x, max_x = GraphicsHelperPanel.get_min_max_x_bound_box_corners(front)
            mins.append(min_x)
            maxs.append(max_x)

        if not back is None:
            min_x, max_x = GraphicsHelperPanel.get_min_max_x_bound_box_corners(back)
            mins.append(min_x)
            maxs.append(max_x)
        
        body_min_x, body_max_x = GraphicsHelperPanel.get_min_max_x_bound_box_corners(body)
        mins.append(body_min_x)
        maxs.append(body_max_x)

        min_x = body.location[0] - min(mins)
        max_x = max(maxs) - body.location[0]
        return max(min_x, max_x)

    @staticmethod
    def get_bogie_position_from_component(bogie, body, half_width):
        body_x = body.location[0]
        bogie_x = bogie.location[0]
        position_from_centre = max(body_x, bogie_x) - min(body_x, bogie_x)
        return half_width - position_from_centre

    @staticmethod 
    def get_car_components(bogies, bodies):
        components = []
        for body in bodies:
            component_bogies = [x for x in bogies if x.loco_graphics_helper_vehicle_properties.bogie_parent_index == body.loco_graphics_helper_vehicle_properties.index]
            if len(component_bogies) != 2:
                components.append((None, None, body))
                continue
            
            front_bogie = component_bogies[0] if component_bogies[0].location[0] > component_bogies[1].location[0] else component_bogies[1]
            back_bogie = component_bogies[1] if component_bogies[0].location[0] > component_bogies[1].location[0] else component_bogies[0]

            components.append((front_bogie, back_bogie, body))
        return components

    @staticmethod
    def blender_to_loco_dist(dist):
        return int(dist * 32 + 0.5)

    def draw_vehicle_panel(self, scene, layout):
        general_properties = scene.loco_graphics_helper_general_properties
        bodies = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "BODY"]
        bodies = sorted(bodies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)
        bogies = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "BOGIE"]
        bogies = sorted(bogies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)

        total_number_of_sprites = 0

        components = self.get_car_components(bogies, bodies)
        if len(components) > 0:     
            row = layout.row()
            row.label("Car(s) details:")

            for component in components:
                front, back, body = component
                idx = body.loco_graphics_helper_vehicle_properties.index
                half_width = self.get_longest_component_edge(front, back, body)

                front_position = 0
                back_position = 0
                front_idx = 255
                back_idx = 255
                warning = None
                if not front is None:
                    front_position = self.get_bogie_position_from_component(front, body, half_width)
                    back_position = self.get_bogie_position_from_component(back, body, half_width)

                    front_idx = front.loco_graphics_helper_vehicle_properties.index - 1
                    back_idx = back.loco_graphics_helper_vehicle_properties.index - 1
                    mid_point_x = (front.location[0] - back.location[0]) / 2 + back.location[0]
                    if not math.isclose(body.location[0], mid_point_x, rel_tol=1e-4):
                        warning = "BODY LOCATION IS NOT AT MID X POINT BETWEEN BOGIES! {}".format(mid_point_x)

                
                row = layout.row()
                row.label(" {}. {}, Half-Width: {}, Front Position: {}, Back Position: {}".format(idx, body.name, self.blender_to_loco_dist(half_width), self.blender_to_loco_dist(front_position), self.blender_to_loco_dist(back_position)))
                row = layout.row()
                row.label("    Body Sprite Index: {}, Front Bogie Sprite Index: {}, Back Bogie Sprite Index: {},".format(idx - 1, front_idx, back_idx))
                if not warning is None:
                    row = layout.row()
                    row.label("    WARNING: {},".format(warning))

        if len(bodies) > 0:
            row = layout.row()
            row.label("Body(s) details:")
            for idx, body in enumerate(bodies):
                row = layout.row()
                number_of_sprites = self.get_number_of_sprites(body)
                row.label(" {}. {}, Number of sprites: {}".format(idx + 1, body.name, number_of_sprites))
                total_number_of_sprites = total_number_of_sprites + number_of_sprites

        if len(bogies) > 0:
            row = layout.row()
            row.label("Bogie(s) details:")
            for idx, bogie in enumerate(bogies):
                row = layout.row()
                number_of_sprites = 0
                if not bogie.loco_graphics_helper_vehicle_properties.is_clone_bogie:
                    number_of_sprites = self.get_number_of_sprites(bogie)
                    total_number_of_sprites = total_number_of_sprites + number_of_sprites
                row.label(" {}. {}, Number of sprites: {}".format(idx + 1, bogie.name, number_of_sprites))

        row = layout.row()
        row.label("Total number of sprites: {}".format(total_number_of_sprites))

        if total_number_of_sprites == 0:
            row = layout.row()
            row.label("NO BODIES OR BOGIES SET!")
            row = layout.row()
            row.label("NOTHING WILL BE RENDERED!")

        row = layout.row()
        text = "Render"
        if general_properties.rendering:
            text = "Failed"
        row.operator("render.loco_vehicle", text=text)
