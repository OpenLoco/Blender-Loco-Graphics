'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

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

    def draw_vehicle_panel(self, scene, layout):
        general_properties = scene.loco_graphics_helper_general_properties

        row = layout.row()

        text = "Render"
        if general_properties.rendering:
            text = "Failed"
        row.operator("render.loco_vehicle", text=text)

class ObjectHelperPanel(bpy.types.Panel):
    bl_label = "Loco Graphics"
    bl_idname = "OBJECT_PT_loco_graphics_helper.objects"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        object_properties = context.object.loco_graphics_helper_object_properties

        row = layout.row()
        row.prop(object_properties, "object_type")
        
        if not "Rig" in context.scene.objects:
            return

        if object_properties.object_type == "CAR":
            self.draw_car_panel(context, layout)
        
        if object_properties.object_type == "BOGIE":
            self.draw_bogie_panel(context, layout)

    def draw_bogie_panel(self, context, layout):
        scene = context.scene
        general_properties = scene.loco_graphics_helper_general_properties
        row = layout.row()

        if not general_properties.render_mode == "VEHICLE":
            row.label("Vehicle Render Mode Required")
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        box = layout.box()

        row = box.row()
        row.label("Track Properties:")

        split = box.split(.50)
        columns = [split.column(), split.column()]
        i = 0
        for sprite_track_flagset in vehicle_properties.sprite_track_flags_list:
            columns[i % 2].row().prop(vehicle_properties, "sprite_track_flags",
                                      index=i, text=sprite_track_flagset.name)
            i += 1

        row = layout.row()

        row.label("Flat Viewing Angles: 32")
        row = layout.row()

        row.label("Sloped Viewing Angles: 32")
        row = layout.row()

        row.prop(vehicle_properties, "index")
        row = layout.row()

        row.prop(vehicle_properties, "number_of_animation_frames")
        row = layout.row()

        row.prop(vehicle_properties, "rotational_symmetry")
        row = layout.row()

    def draw_car_panel(self, context, layout):
        scene = context.scene
        general_properties = scene.loco_graphics_helper_general_properties
        row = layout.row()

        if not general_properties.render_mode == "VEHICLE":
            row.label("Vehicle Render Mode Required")
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        box = layout.box()

        row = box.row()
        row.label("Track Properties:")

        split = box.split(.50)
        columns = [split.column(), split.column()]
        i = 0
        for sprite_track_flagset in vehicle_properties.sprite_track_flags_list:
            columns[i % 2].row().prop(vehicle_properties, "sprite_track_flags",
                                      index=i, text=sprite_track_flagset.name)
            i += 1

        row = layout.row()

        row.label("Flat Viewing Angles:")
        row = layout.row()
        row.prop(vehicle_properties, "flat_viewing_angles", text="")
        row = layout.row()

        row.label("Sloped Viewing Angles:")
        row = layout.row()
        row.prop(vehicle_properties, "sloped_viewing_angles", text="")
        row = layout.row()

        row.prop(vehicle_properties, "roll_angle")
        row = layout.row()

        row.prop(vehicle_properties, "index")
        row = layout.row()

        row.prop(vehicle_properties, "number_of_animation_frames")
        row = layout.row()

        if vehicle_properties.number_of_animation_frames != 1 and vehicle_properties.roll_angle != 0:
            row.label("WARNING CANNOT HAVE BOTH ANIMATION FRAMES AND ROLL ANGLE SET")
            row = layout.row()

        row.prop(vehicle_properties, "rotational_symmetry")
        row = layout.row()

        row.prop(vehicle_properties, "braking_lights")
        row = layout.row()
        if vehicle_properties.braking_lights and vehicle_properties.roll_angle != 0:
            row.label("WARNING CANNOT HAVE BOTH BRAKING LIGHTS AND ROLL ANGLE SET") 
            row = layout.row()
