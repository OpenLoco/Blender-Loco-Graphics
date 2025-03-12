'''
Copyright (c) 2024 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from .track import is_road, is_rail, TrackPiece, get_layer_names, get_num_layers
from .angle_sections.track import TrackPieceType, RoadPieceType, track_piece_manifest, TrackType

class LocoObjectHelperPanel(bpy.types.Panel):
    bl_label = "Loco Graphics"
    bl_idname = "OBJECT_PT_loco_graphics_helper.objects"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        object_properties = context.object.loco_graphics_helper_object_properties
        object_type = object_properties.object_type

        # this connects a track layer object to its parent object
        track_object = context.object
        scene = context.scene
        while track_object.parent is not None:
            track_object = track_object.parent
            if track_object.loco_graphics_helper_object_properties.object_type == "TRACK_PIECE":
                break
        if track_object == scene or track_object == context.object:
            track_object = None

        row = layout.row()
        if not "Rig" in context.scene.objects:
            row.label("Tool is not intialised.")
            return

        # if it's a track layer object, force the type to NONE and don't show the property
        if track_object and track_object.loco_graphics_helper_object_properties.object_type == "TRACK_PIECE":
            pass
        else:
            row.prop(object_properties, "object_type")

        if object_type == "BODY":
            self.draw_body_panel(context, layout)
        
        if object_type == "BOGIE":
            self.draw_bogie_panel(context, layout)

        if object_type == "CAR":
            self.draw_car_panel(context, layout)

        # if it's a track layer object, show the track properties of the track piece object
        if track_object and track_object.loco_graphics_helper_object_properties.object_type == "TRACK_PIECE":
            self.draw_piece_panel(context, track_object, layout)
        elif object_type == "TRACK_PIECE":
            self.draw_piece_panel(context, context.object, layout)

    @staticmethod
    def wrong_render_mode(context, layout, mode):
        scene = context.scene
        general_properties = scene.loco_graphics_helper_general_properties
        
        if general_properties.render_mode != mode:
            row = layout.row()
            row.label("{} render mode required".format(mode))
            return True
        return False

    def draw_piece_panel(self, context, track_object, layout):

        if self.wrong_render_mode(context, layout, "TRACK"):
            return

        # track piece's properties
        track_piece_properties = track_object.loco_graphics_helper_track_piece_properties
        if is_road():
            row = layout.row()
            row.prop(track_piece_properties,"road_piece")
            row = layout.row()
            row.prop(track_piece_properties,"reversed")
        else:
            row = layout.row()
            row.prop(track_piece_properties,"track_piece")
        
        piece_name = track_piece_properties.road_piece if is_road() else track_piece_properties.track_piece
        piece_type = RoadPieceType[piece_name] if is_road() else TrackPieceType[piece_name]
        
        if piece_type.value <= 0:
            return
        manifest = track_piece_manifest[piece_type.value]
        track_piece = TrackPiece(manifest, track_object)
        box = layout.box()
        box.label("Layers:")
        split = box.split(.50)
        columns = [split.column(), split.column()]
        for i in range(get_num_layers(manifest.sprite_type)):
            names = get_layer_names(i + manifest.base_layer_name)
            # track layer's properties
            columns[i % 2].row().prop(context.object.loco_graphics_helper_track_piece_properties, "layers",
                                      index=i, text=names[0])
        box = layout.box()
        col = box.column()
        for i in range(track_piece.num_layers):
            col.label("{} layer:".format(track_piece.layer_names[i]))
            if len(track_piece.layer_objects[i]) == 0:
                col.label("  No model set. Sprites will be blank.")
            else:
                col.label("  "+", ".join([x.name for x in track_piece.layer_objects[i]]))

    def draw_layer_panel(self, context, layout):
        row = layout.row()

        if self.wrong_render_mode(context, layout, "TRACK"):
            return

        track_piece_properties = context.object.loco_graphics_helper_track_piece_properties

        parent = context.object.parent
        parent_properties = parent.loco_graphics_helper_track_piece_properties
        piece_name = parent_properties.road_piece if is_road() else parent_properties.track_piece
        piece_type = RoadPieceType[piece_name] if is_road() else TrackPieceType[piece_name]
        if piece_type.value <= 0:
            return
        manifest = track_piece_manifest[piece_type.value]
        box = layout.box()
        box.label("Layers:")
        split = box.split(.50)
        columns = [split.column(), split.column()]
        for i in range(get_num_layers(manifest.sprite_type)):
            names = get_layer_names(i + manifest.base_layer_name)
            columns[i % 2].row().prop(track_piece_properties, "layers",
                                      index=i, text=names[0])

    def draw_car_panel(self, context, layout):
        row = layout.row()

        if self.wrong_render_mode(context, layout, "VEHICLE"):
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        row.prop(vehicle_properties, "index")
        row = layout.row()

    def draw_bogie_panel(self, context, layout):

        if self.wrong_render_mode(context, layout, "VEHICLE"):
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        row = layout.row()
        row.prop(vehicle_properties, "null_component")
        row = layout.row()

        if vehicle_properties.null_component:
            return

        row.prop(vehicle_properties, "index")
        row = layout.row()

        row.prop(vehicle_properties, "is_clone")
        row = layout.row()

        row.prop(vehicle_properties, "is_inverted")
        row = layout.row()

        if vehicle_properties.is_clone:
            return

        row.prop(vehicle_properties, "render_sprite")
        row = layout.row()

        box = layout.box()

        row = box.row()
        row.label("Sprite:")

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

        row.prop(vehicle_properties, "number_of_animation_frames")
        row = layout.row()

        row.prop(vehicle_properties, "rotational_symmetry")
        row = layout.row()

        row.prop(vehicle_properties, "bounding_box_override")

    def draw_body_panel(self, context, layout):

        if self.wrong_render_mode(context, layout, "VEHICLE"):
            return

        vehicle_properties = context.object.loco_graphics_helper_vehicle_properties

        row = layout.row()
        row.prop(vehicle_properties, "null_component")

        if vehicle_properties.null_component:
            return

        row = layout.row()
        row.prop(vehicle_properties, "index")
        row = layout.row()

        row.prop(vehicle_properties, "is_clone")
        row = layout.row()

        row.prop(vehicle_properties, "is_inverted")
        row = layout.row()

        if vehicle_properties.is_clone:
            return

        row.prop(vehicle_properties, "render_sprite")
        row = layout.row()

        box = layout.box()

        box.label("Sprites:")

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

        row.prop(vehicle_properties, "tilt_angle")
        row = layout.row()

        row.prop(vehicle_properties, "number_of_animation_frames")
        row = layout.row()

        if vehicle_properties.number_of_animation_frames != 1 and vehicle_properties.tilt_angle != 0:
            row.label("WARNING: cannot have tilt frames and animation frames")
            row = layout.row()

        row.prop(vehicle_properties, "rotational_symmetry")
        row = layout.row()

        row.prop(vehicle_properties, "braking_lights")
        row = layout.row()
        if vehicle_properties.braking_lights and vehicle_properties.roll_angle != 0:
            row.label("WARNING: cannot have brake lights and tilt frames") 
            row = layout.row()

        row.prop(vehicle_properties, "is_airplane")
        row = layout.row()

        row.prop(vehicle_properties, "bounding_box_override")
