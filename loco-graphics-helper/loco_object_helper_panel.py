'''
Copyright (c) 2024 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy

class LocoObjectHelperPanel(bpy.types.Panel):
    bl_label = "Loco Graphics"
    bl_idname = "OBJECT_PT_loco_graphics_helper.objects"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        object_properties = context.object.loco_graphics_helper_object_properties

        row = layout.row()
        if not "Rig" in context.scene.objects:
            row.label("Tool is not intialised.")
            return
        row.prop(object_properties, "object_type")

        if object_properties.object_type == "BODY":
            self.draw_body_panel(context, layout)
        
        if object_properties.object_type == "BOGIE":
            self.draw_bogie_panel(context, layout)

        if object_properties.object_type == "CAR":
            self.draw_car_panel(context, layout)

    def draw_car_panel(self, context, layout):
        scene = context.scene
        general_properties = scene.loco_graphics_helper_general_properties
        row = layout.row()

        if not general_properties.render_mode == "VEHICLE":
            row.label("Vehicle Render Mode Required")
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        row.prop(vehicle_properties, "index")
        row = layout.row()

    def draw_bogie_panel(self, context, layout):
        scene = context.scene
        general_properties = scene.loco_graphics_helper_general_properties
        row = layout.row()

        if not general_properties.render_mode == "VEHICLE":
            row.label("Vehicle Render Mode Required")
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        row.prop(vehicle_properties, "is_clone")
        row = layout.row()

        row.prop(vehicle_properties, "is_inverted")
        row = layout.row()

        if vehicle_properties.is_clone:
            row.prop(vehicle_properties, "index",text="Clone of bogie index:")
            row = layout.row()
            return

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

    def draw_body_panel(self, context, layout):
        scene = context.scene
        general_properties = scene.loco_graphics_helper_general_properties
        row = layout.row()

        if not general_properties.render_mode == "VEHICLE":
            row.label("Vehicle Render Mode Required")
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        row.prop(vehicle_properties, "is_clone")
        row = layout.row()

        row.prop(vehicle_properties, "is_inverted")
        row = layout.row()

        if vehicle_properties.is_clone:
            row.prop(vehicle_properties, "index",text="Clone of body index:")
            row = layout.row()
            return
        
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

        row.prop(vehicle_properties, "is_airplane")
        row = layout.row()
