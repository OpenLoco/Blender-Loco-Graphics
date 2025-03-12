'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from mathutils import Vector
from typing import List
from .angle_sections.track import *

def track_properties():
    return bpy.context.scene.loco_graphics_helper_track_properties

def get_num_layers(sprite_type):
    if sprite_type == "UI" or sprite_type == "NULL":
        return 1
    object_type = TrackType[track_properties().track_type]
    map = {
    TrackType.RAIL: {"FLAT": 3, "SLOPE": 1},
    TrackType.ROAD: {"FLAT": 1, "SLOPE": 1},
    TrackType.TRAM: {"FLAT": 3, "SLOPE": 3}
    }
    return map[object_type][sprite_type]

# used to determine available pieces
def is_road():
    object_type = TrackType[track_properties().track_type]
    if object_type == TrackType.TRAM:
        return True
    return object_type == TrackType.ROAD

# used to determine layer names
def is_rail():
    object_type = TrackType[track_properties().track_type]
    if object_type == TrackType.TRAM:
        return True
    return object_type == TrackType.RAIL

def get_layer_names(layer):
    if is_rail():
        return track_layer_names[layer]
    else:
        return road_layer_names[layer]

class TrackPiece():
    track_piece = 0
    root_object = None
    num_layers = 0
    layer_objects = []
    layer_names = []
    manifest = None
    render_sprite = False
    location = [0,0,0]
    def __init__(self, manifest, root_object = None):
        self.manifest = manifest
        self.track_piece = manifest.track_piece
        self.num_layers = get_num_layers(manifest.sprite_type)
        self.layer_names = [get_layer_names(manifest.base_layer_name + i)[0] for i in range(self.num_layers)]
        self.layer_objects = [[] for i in range(self.num_layers)]
        if root_object is not None:
            self.set_root_object(root_object)

    def set_root_object(self, object):
        self.root_object = object
        self.location = object.matrix_world.translation
        self.render_sprite = object.loco_graphics_helper_track_piece_properties.render_sprite
        objects = object.children
        for i in range(self.num_layers):
            self.layer_objects[i] = [x for x in objects if x.loco_graphics_helper_track_piece_properties.layers[i]]
            if (object.loco_graphics_helper_track_piece_properties.layers[i]):
                self.layer_objects[i].append(object)

def get_valid_pieces():
    piece_list = RoadPieceType if is_road() else TrackPieceType # the enum with the list of pieces
    return [a.value for a in piece_list if a.value > 0]

def get_track_pieces(objects) -> List[TrackPiece]:
    pieces = [TrackPiece(a) for a in track_piece_manifest]
    piece_type_property = "road_piece" if is_road() else "track_piece" # the property in track_piece_properties
    for object in objects:
        if piece_type_property in object.loco_graphics_helper_track_piece_properties:
            piece_number = object.loco_graphics_helper_track_piece_properties[piece_type_property]
            if piece_number > 0:
                pieces[piece_number].set_root_object(object)

    return pieces