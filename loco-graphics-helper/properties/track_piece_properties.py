'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from ..angle_sections.track import track_piece_manifest, TrackPieceType, RoadPieceType, max_layers

class TrackPieceProperties(bpy.types.PropertyGroup):
    track_piece = bpy.props.EnumProperty(
        name="Track Piece",
        items=tuple((enum_item.name,track_piece_manifest[enum_item.value].name,"",enum_item.value) for enum_item in TrackPieceType),
        default="NONE"
    )
    road_piece = bpy.props.EnumProperty(
        name="Road Piece",
        items=tuple((enum_item.name,track_piece_manifest[enum_item.value].name,"",enum_item.value) for enum_item in RoadPieceType),
        default="NONE"
    )

    reversed = bpy.props.BoolProperty(
        name="Reverse Road",
        description="If set, the normal direction of travel is toward the image Southwest. If unset, normal direction of travel is toward the image Northeast, or is two-way",
        default=False)

    layers = bpy.props.BoolVectorProperty(
        name="Track Layers",
        default=[False for _ in range(max_layers)],
        description="Which layers this model is rendered as",
        size=max_layers
    )

    render_sprite = bpy.props.BoolProperty(
        name="Render Track piece",
        description="Include this track piece when batch rendering",
        default=True
    )

def register_track_piece_properties():
    bpy.types.Object.loco_graphics_helper_track_piece_properties = bpy.props.PointerProperty(
        type=TrackPieceProperties)


def unregister_track_piece_properties():
    del bpy.types.Object.loco_graphics_helper_track_piece_properties
