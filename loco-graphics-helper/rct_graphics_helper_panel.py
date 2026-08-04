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

from .vehicle import get_car_components, VehicleComponent, SubComponent, get_number_of_sprites, get_half_width

class RepairConfirmOperator(bpy.types.Operator):
    """This action will clear out the default camera and light. Changes made to the rig object, compositor nodes and recolorable materials will be lost."""
    bl_idname = "loco_graphics_helper.repair_confirm"
    bl_label = "Do you want to (re)create the base scene?"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        bpy.ops.loco_eevee.initialize()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class GraphicsHelperPanel(bpy.types.Panel):
    bl_label = "Loco Graphics Helper"
    bl_idname = "VIEW3D_PT_loco_graphics_helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
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
        row.label(text="General:")

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
        row.label(text="Dither Palette:")

        row = layout.row()
        row.prop(properties, "palette", text="")

        if properties.palette == "CUSTOM":
            box = layout.box()
            split = box.split(factor=.50)
            columns = [split.column(), split.column()]
            i = 0
            for color in palette_colors:
                details = palette_colors_details[color]
                columns[i % 2].row().prop(properties, "custom_palette_colors",
                                          index=i, text=details["title"])
                i += 1

        row = layout.row()
        row.label(text="Object Type:")

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
        row.operator("loco_eevee.render_tiles", text=text)

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
        row.operator("loco_eevee.render_walls", text=text)

    def draw_track_panel(self, scene, layout):
        properties = scene.loco_graphics_helper_track_properties
        general_properties = scene.loco_graphics_helper_general_properties

        row = layout.row()
        row.label(text="Work in progress")
        
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

    @staticmethod
    def calculate_precision(x):
        return [y for y in range(8) if (1 << y) == int(x)][0] - 2

    def draw_vehicle_panel(self, scene, layout):
        general_properties = scene.loco_graphics_helper_general_properties

        row = layout.row()
        row.prop(general_properties,"transport_mode")
        
        cars = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "CAR"]
        cars = sorted(cars, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)

        total_number_of_sprites = 0
        renderable_sprites = 0

        components = get_car_components(cars)
        if len(components) == 0:
            return
        row = layout.row()
        row.label(text="Car(s) details:")

        for component in components:
            front = component.get_object(SubComponent.FRONT)
            back = component.get_object(SubComponent.BACK)
            body = component.get_object(SubComponent.BODY)
            idx = body.loco_graphics_helper_vehicle_properties.index

            front_position = -1.0/32
            back_position = -1.0/32
            body_idx = component.get_component_index(SubComponent.BODY)
            front_idx = component.get_component_index(SubComponent.FRONT)
            back_idx = component.get_component_index(SubComponent.BACK)
            warning = None
            anim_location = 0
            front_name = '' if front is None else front.name
            back_name = '' if back is None else back.name
            mid_point_x = component.get_preferred_body_midpoint()
            #TODO 2026-08-03: fix this to accurately determine when the body origin is not halfway between the bogies, as well as determine the bogie positions accurately
            if body.loco_graphics_helper_vehicle_properties.bounding_box_override is None and not math.isclose(body.matrix_world.translation[0], mid_point_x, rel_tol=1e-4):
                warning = "Body location is not at midpoint, off by {}".format(mid_point_x)

            if front is not None:
                front_position = component.get_bogie_position(SubComponent.FRONT)
            if back is not None:
                back_position = component.get_bogie_position(SubComponent.BACK)

                #TODO 2026-08-03: why is this in the back classmethod
                anim_location = component.get_emitter_x()
                if anim_location is not None and (anim_location > 255 or anim_location < 0):
                    warning = "Emitter is too far from bogies"
                    anim_location = 255
            elif body.loco_graphics_helper_properties.is_airplane:
                front_idx = 0
                back_idx = 255
                front_position = 0
                back_position = 0


            box = layout.box()
            box.label(text="Car {}: {}".format(component.car.loco_graphics_helper_vehicle_properties.index, component.car.name))
            col = box.column()
            col.label(text="{}, {}, {}".format(body.name, front_name, back_name))
            col.label(text="  Front Position: {}".format(self.blender_to_loco_dist(front_position)))
            col.label(text="  Back Position: {}".format(self.blender_to_loco_dist(back_position)))
            col.label(text="  Front Bogie Sprite Index: {}".format(front_idx))
            col.label(text="  Back Bogie Sprite Index: {}".format(back_idx))
            col.label(text="  Body Sprite Index: {}".format(body_idx))
            if not anim_location is None:
                col.label(text="  Emitter Horizontal Position: {}".format(anim_location))

            if warning is not None:
                row = box.row()
                row.label(text="    WARNING: {},".format(warning))

        bodies = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "BODY" and not x.loco_graphics_helper_vehicle_properties.is_clone and get_number_of_sprites(x) > 0]
        bodies = sorted(bodies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)
        
        if len(bodies) > 0:
            for body in bodies:
                number_of_sprites = get_number_of_sprites(body)
                total_number_of_sprites += number_of_sprites

                half_width = -1.0/32
                car = None
                if body.loco_graphics_helper_vehicle_properties.bounding_box_override:
                    half_width = get_half_width(body.loco_graphics_helper_vehicle_properties.bounding_box_override)
                for component in components:
                    if component.body == body:
                        car = component
                        half_width = component.get_half_width()
                        break
                emitter_z = car.get_emitter_z()

                if number_of_sprites == 0:
                    continue

                if body.loco_graphics_helper_vehicle_properties.render_sprite:
                    renderable_sprites += number_of_sprites

                box = layout.box()
                row = box.row()
                row.label(text="Body {}: {}".format(body.loco_graphics_helper_vehicle_properties.index, body.name))
                row.prop(body.loco_graphics_helper_vehicle_properties, "render_sprite")
                col = box.column()
                col.label(text="  Flat Rotation Frames: {}".format(body.loco_graphics_helper_vehicle_properties.flat_viewing_angles))
                col.label(text="  Sloped Rotation Frames: {}".format(body.loco_graphics_helper_vehicle_properties.sloped_viewing_angles))
                col.label(text="  Tilt Frames: {}".format(3 if body.loco_graphics_helper_vehicle_properties.roll_angle != 0 else 1))
                col.label(text="  Half-Length: {}{}".format(self.blender_to_loco_dist(half_width), " (override)" if body.loco_graphics_helper_vehicle_properties.bounding_box_override else ""))
                col.label(text="  Flat Yaw Accuracy: {}".format(self.calculate_precision(body.loco_graphics_helper_vehicle_properties.flat_viewing_angles)))
                col.label(text="  Sloped Yaw Accuracy: {}".format(self.calculate_precision(body.loco_graphics_helper_vehicle_properties.sloped_viewing_angles)))
                col.label(text="  Frames per Viewing Angle: {}".format(0))
                col.label(text="  Number of sprites: {}".format(number_of_sprites))
                if not emitter_z is None:
                    col.label(text="  Emitter Vertical Position: {}".format(emitter_z))

        bogies = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "BOGIE" and not x.loco_graphics_helper_vehicle_properties.is_clone and get_number_of_sprites(x) > 0]
        bogies = sorted(bogies, key=lambda x: x.loco_graphics_helper_vehicle_properties.index)

        if len(bogies) > 0:
            for bogie in bogies:
                number_of_sprites = get_number_of_sprites(bogie)
                total_number_of_sprites += number_of_sprites

                if bogie.loco_graphics_helper_vehicle_properties.render_sprite:
                    renderable_sprites += number_of_sprites

                box = layout.box()
                row = box.row()
                row.label(text="Bogie {}: {}".format(bogie.loco_graphics_helper_vehicle_properties.index, bogie.name))
                row.prop(bogie.loco_graphics_helper_vehicle_properties, "render_sprite")
                col = box.column()
                col.label(text="  Number of sprites: {}".format(number_of_sprites))

        row = layout.row()
        if renderable_sprites > 0:
            row.label(text="Sprites to render: {}".format(renderable_sprites))
        else:
            row.label(text="WARNING: 0 sprites to render")

        row = layout.row()
        text = "Render"
        if general_properties.rendering:
            text = "Failed"
        row.operator("loco_eevee.render_vehicle", text=text)

def register_panel():
    bpy.utils.register_class(GraphicsHelperPanel)
    bpy.utils.register_class(RepairConfirmOperator)

def unregister_panel():
    bpy.utils.unregister_class(GraphicsHelperPanel)
    bpy.utils.unregister_class(RepairConfirmOperator)
