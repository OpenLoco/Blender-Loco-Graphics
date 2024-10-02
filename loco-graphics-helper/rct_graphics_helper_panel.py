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

from .vehicle import get_car_components, VehicleComponent, SubComponent

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
    def blender_to_loco_dist(dist):
        return int(dist * 32 + 0.5)

    def draw_vehicle_panel(self, scene, layout):
        general_properties = scene.loco_graphics_helper_general_properties
        
        cars = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "CAR"]
        cars = sorted(cars, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)

        total_number_of_sprites = 0

        components = get_car_components(cars)
        if len(components) == 0:
            return   
        row = layout.row()
        row.label("Car(s) details:")

        for component in components:
            front = component.get_object(SubComponent.FRONT)
            back = component.get_object(SubComponent.BACK)
            body = component.get_object(SubComponent.BODY)
            idx = body.loco_graphics_helper_vehicle_properties.index

            front_position = 0
            back_position = 0
            body_idx = idx - 1 + 180 if body.loco_graphics_helper_vehicle_properties.is_inverted else idx - 1
            front_idx = 255
            back_idx = 255
            warning = None
            anim_location = 0
            front_name = '' if front is None else front.name
            back_name = '' if back is None else back.name
            mid_point_x = component.get_preferred_body_midpoint()
            if not math.isclose(body.matrix_world.translation[0], mid_point_x, rel_tol=1e-4):
                warning = "BODY LOCATION IS NOT AT PREFERRED MID X POINT! {}".format(mid_point_x)

            if not front is None:
                front_position = component.get_bogie_position(SubComponent.FRONT)
                back_position = component.get_bogie_position(SubComponent.BACK)

                if component.get_number_of_sprites(SubComponent.FRONT) != 0:
                    front_idx = front.loco_graphics_helper_vehicle_properties.index - 1
                    front_idx = front_idx + 180 if front.loco_graphics_helper_vehicle_properties.is_inverted else front_idx

                if component.get_number_of_sprites(SubComponent.BACK) != 0:
                    back_idx = back.loco_graphics_helper_vehicle_properties.index - 1
                    back_idx = back_idx + 180 if front.loco_graphics_helper_vehicle_properties.is_inverted else back_idx

                anim_location = component.get_animation_location()
                if anim_location > 255 or anim_location < 0:
                    warning = "Animation is too far from bogies"
                    anim_location = 255
            elif body.loco_graphics_helper_vehicle_properties.is_airplane:
                front_idx = 0
            
            row = layout.row()
            row.label("{}. {}, {}, {}, {}".format(component.car.loco_graphics_helper_vehicle_properties.index - 1, component.car.name, body.name, front_name, back_name))
            row = layout.row()
            row.label("  Front Position: {}".format(self.blender_to_loco_dist(front_position)))
            row = layout.row()
            row.label("  Back Position: {}".format(self.blender_to_loco_dist(back_position)))
            row = layout.row()
            row.label("  Front Bogie Sprite Index: {}".format(front_idx))
            row = layout.row()
            row.label("  Back Bogie Sprite Index: {}".format(back_idx))
            row = layout.row()
            row.label("  Body Sprite Index: {}".format(body_idx))
            row = layout.row()
            row.label("  Animation Position: {}".format(anim_location))

            if not warning is None:
                row = layout.row()
                row.label("    WARNING: {},".format(warning))

        row = layout.row()
        row.label("Body(s) details:")
        components = sorted(components, key=lambda x: x.body.loco_graphics_helper_vehicle_properties.index)
        for component in components:
            body = component.body
            if body is None:
                continue
            if body.loco_graphics_helper_vehicle_properties.is_clone:
                continue
            number_of_sprites = component.get_number_of_sprites(SubComponent.BODY)
            total_number_of_sprites = total_number_of_sprites + number_of_sprites

            if number_of_sprites == 0:
                continue

            half_width = component.get_half_width()
            row = layout.row()
            row.label("{}. {}".format(body.loco_graphics_helper_vehicle_properties.index, body.name))
            row = layout.row()
            row.label("  Half-Width: {}".format(self.blender_to_loco_dist(half_width)))
            row = layout.row()
            row.label("  Number of sprites: {}".format(number_of_sprites))

        bogies = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "BOGIE" and not x.loco_graphics_helper_vehicle_properties.is_clone]
        bogies = sorted(bogies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)
        
        row = layout.row()
        row.label("Bogie(s) details:")
        for bogie in bogies:
            car = None
            sub_component = None
            for component in components:
                if component.front == bogie:
                    car = component
                    sub_component = SubComponent.FRONT
                    break
                if component.back == bogie:
                    car = component
                    sub_component = SubComponent.BACK
                    break
            if car is None:
                continue
            
            number_of_sprites = car.get_number_of_sprites(sub_component)
            total_number_of_sprites = total_number_of_sprites + number_of_sprites

            if number_of_sprites == 0:
                continue

            half_width = component.get_half_width()
            row = layout.row()
            row.label("{}. {}".format(bogie.loco_graphics_helper_vehicle_properties.index, bogie.name))
            row = layout.row()
            row.label("  Number of sprites: {}".format(number_of_sprites))
        
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
