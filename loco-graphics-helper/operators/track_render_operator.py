'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from .render_operator import RCTRender
from ..track import get_valid_pieces, get_track_pieces


class TrackPieceLayer():
    def __init__(self, location, objects, manifest):
        self.location = location
        self.manifest = manifest
        self.objects = objects

class RenderTrack(RCTRender, bpy.types.Operator):
    bl_idname = "render.loco_track"
    bl_label = "Render Loco Track"

    def create_task(self, context):
        scene = context.scene
        props = scene.loco_graphics_helper_track_properties
        general_props = scene.loco_graphics_helper_general_properties
        
        self.task_builder.clear()
        
        self.task_builder.set_anti_aliasing_with_background(
            context.scene.render.use_antialiasing, general_props.anti_alias_with_background, general_props.maintain_aliased_silhouette)
            
        self.task_builder.set_output_index(general_props.out_start_index)
        self.task_builder.set_recolorables(general_props.number_of_recolorables)
        self.task_builder.set_cast_shadows(general_props.cast_shadows)
        
        self.task_builder.set_palette(self.palette_manager.get_base_palette(
            general_props.palette, general_props.number_of_recolorables, "FULL"))

        valid_pieces = get_valid_pieces()

        track_pieces = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "TRACK_PIECE" and not x.loco_graphics_helper_track_piece_properties.reversed]

        ndot_pieces = get_track_pieces(track_pieces)
        for i in valid_pieces:
            self.add_track_piece(ndot_pieces[i])

        if props.one_way:
            reverse_pieces = [x for x in scene.objects if x.loco_graphics_helper_object_properties.object_type == "TRACK_PIECE" and x.loco_graphics_helper_track_piece_properties.reversed]
            rdot_pieces = get_track_pieces(reverse_pieces)
            for i in valid_pieces:
                self.add_track_piece(rdot_pieces[i])

        return self.task_builder.create_task(context)

    def add_track_piece(self, track_piece):
        num_frames = track_piece.manifest.get_sprites_per_layer() * track_piece.num_layers
        if track_piece.render_sprite:
            for i in range(track_piece.num_layers):
                self.add_layer(track_piece, i)
        else:
            self.task_builder.output_flags = 0
            self.task_builder.add_null_frames(num_frames)
    
    def add_layer(self, track_piece, layer):
        """track_piece.location"""
        manifest = track_piece.manifest
        target_object = TrackPieceLayer((0,0,0),track_piece.layer_objects[layer], manifest)
        self.task_builder.output_flags = 1
        # self.task_builder.output_prefix = "{}_{}".format(manifest.name, track_piece.layer_names[layer])
        self.task_builder.target_object = target_object
        self.task_builder.mirror_x = False
        self.task_builder.set_size(manifest.grid_size[0], manifest.grid_size[1], False)
        self.task_builder.add_viewing_angles(manifest.angles, 0, 1, manifest.symmetric, "TRACK")
        
        if manifest.render_mirror:
            self.task_builder.mirror_x = True
            self.task_builder.add_viewing_angles(manifest.angles, 0, 1, manifest.symmetric, "TRACK")
        