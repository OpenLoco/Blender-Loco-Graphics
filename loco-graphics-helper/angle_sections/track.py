'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

from enum import Enum

track_angle_sections_names = [
    "VEHICLE_SPRITE_FLAG_FLAT",
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES",
    "VEHICLE_SPRITE_FLAG_STEEP_SLOPES",
]

# is_transition, number_rotation_frames, angle
track_angle_sections = {
    "VEHICLE_SPRITE_FLAG_FLAT": [
        [False, 32, 0]
    ],
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES": [
        [True, 4, 11.1026 / 2],
        [True, 4, -11.1026 / 2],
        [False, 4, 22.2052 / 2],
        [False, 4, -22.2052 / 2]
    ],
    "VEHICLE_SPRITE_FLAG_STEEP_SLOPES": [
        [True, 4, 11.1026 + 11.1026 / 2],
        [True, 4, -11.1026 - 11.1026 / 2],
        [False, 4, 22.2052],
        [False, 4, -22.2052]
    ],
}

# note to self: images are ordered by sequence FIRST then angle SECOND
"""
layer_names = [
    ["Model"],
    ["Pickup Icon", "Placement Icon"],
    ["Ballast", "Ties", "Rails"]
]

layer_descriptions = [
    ["Icon Model"],
    ["Icon, drawn as train pickup button", "Icon, drawn as train placement button"],
    ["Ballast, drawn above terrain or bridge. Sloped tracks use only this layer, sloped tram track still use all three.", "Ties, drawn above ballast", "Rails, drawn above ties"],
]
"""

max_layers = 3

track_layer_names = [
    ("Spinning Icon","Icon used for tab icon in track building and vehicle purchase windows"),
    ("Pickup Icon", "Icon for pick up vehicle button"),
    ("Placement Icon", "Icon for place vehicle button"),
    ("Ballast","Ballast is drawn above surface and below all other layers"),
    ("Ties","Ties is drawn above ballast and below rail and road layer"),
    ("Rails", "Rails is drawn above ties and road layer"),
    ("Combined", "")
]

road_layer_names = [
    ("Spinning Icon","Icon used for tab icon in track building and vehicle purchase windows"),
    ("Pickup Icon", "Icon for pick up vehicle button"),
    ("Placement Icon", "Icon for place vehicle button"),
    ("Road", "Road is drawn above ties and below rails layer"),
    ("Road", "Road is drawn above ties and below rails layer"),
    ("Road", "Road is drawn above ties and below rails layer"),
    ("Road", "Road is drawn above ties and below rails layer")
]

class TrackType(Enum):
    RAIL = 0
    ROAD = 1
    TRAM = 2

# these are not the OpenLoco track piece IDs. These are the index of the piece in the manifest
# the enum names and number of enum items must be the same between the two
# Values of -1 do not show up in blender enum properties. This is used to filter invalid entries
class TrackPieceType(Enum):
    NONE = 0
    PREVIEW = 1
    PICKUP = 2
    PLACE = 3
    STRAIGHT = 4
    ROAD_CURVE_VERY_SMALL = -1
    T_INTERSECTION = -1
    FOUR_WAY_INTERSECTION = -1
    CURVE_SMALL = 8
    CURVE_SMALL_SLOPE_SHALLOW_UP = 9
    CURVE_SMALL_SLOPE_SHALLOW_DOWN = 10
    CURVE_SMALL_SLOPE_STEEP_UP = 11
    CURVE_SMALL_SLOPE_STEEP_DOWN = 12
    CURVE = 13
    SLOPE_SHALLOW = 14
    SLOPE_STEEP = 15
    CURVE_DIAG = 16
    DIAG_STRAIGHT = 17
    S_BEND = 18
    TRACK_CURVE_VERY_SMALL = 19

class RoadPieceType(Enum):
    NONE = 0
    PREVIEW = 1
    PICKUP = 2
    PLACE = 3
    STRAIGHT = 4
    ROAD_CURVE_VERY_SMALL = 5
    T_INTERSECTION = 6
    FOUR_WAY_INTERSECTION = 7
    CURVE_SMALL = 8
    CURVE_SMALL_SLOPE_SHALLOW_UP = -1
    CURVE_SMALL_SLOPE_SHALLOW_DOWN = -1
    CURVE_SMALL_SLOPE_STEEP_UP = -1
    CURVE_SMALL_SLOPE_STEEP_DOWN = -1
    CURVE = -1
    SLOPE_SHALLOW = 14
    SLOPE_STEEP = 15
    CURVE_DIAG = -1
    DIAG_STRAIGHT = -1
    S_BEND = -1
    TRACK_CURVE_VERY_SMALL = -1

default_manifest = {
    "name": "default track type",
    "angles": 4,
    "symmetric": False,
    "render_mirror": False,
    "grid_size": [1,1],
    "subposition_order": [0],
    "subposition_y_offset": None,
    "sprite_type": "NULL",
    "canvas_size": None,
    "camera_world_offset": [0.5, 0 , 0], # tile X, tile Y, smallZ
    "base_layer_name": 3
}

class TrackPieceManifest:
    track_piece = 0
    name= "null track type"
    angles = 4
    symmetric = False
    render_mirror = False
    grid_size=  [1,1]
    subposition_order = [0]
    subposition_y_offset = [0]
    sprite_type = "NULL"
    canvas_size = None
    camera_world_offset = [0,0,0]
    base_layer_name = 3
    
    def __init__(self, input, piece):
        self.track_piece = piece
        for key in default_manifest.keys():
            if key in input:
                setattr(self, key, input[key])
        if self.canvas_size == None:
            self.canvas_size = [max(self.grid_size[0],self.grid_size[1])*64 for _ in range(2)]
        if self.subposition_y_offset == None:
            self.subposition_y_offset = [0 for _ in range(len(self.subposition_order))]
    def get_sprites_per_layer(self):
        sprites = self.angles / (2 if self.symmetric else 1)
        sprites *= len(self.subposition_order)
        sprites *= 2 if self.render_mirror else 1
        return int(sprites)
    def get_output_order(self):
        order = []
        for i in range(self.grid_size[0] * self.grid_size[1]):
            if i in self.subposition_order:
                order.append(int(self.subposition_order.index(i)))
            else:
                # a negative number so small no project file would ever hit it
                order.append(-99999)
        return order

track_piece_manifest = [
    {
    "angles": 0,
    "name": "None"
    },
    { # Tab icon when building track type
        "name": "Spinning Preview",
        "angles": 32,
        "symmetric": True,
        "grid_size": [1,1],
        "subposition_order": [0],
        "sprite_type": "UI",
        "canvas_size": [29,22],
        "camera_world_offset": [0, 0, 0],
        "base_layer_name": 0
    },
    { # vehicle UI icons for picking up and placing vehicle
        "name": "Pickup icon",
        "angles": 1,
        "grid_size": [1,1],
        "subposition_order": [0],
        "sprite_type": "UI",
        "canvas_size": [20,20],
        "camera_world_offset": [0, 0, 0],
        "base_layer_name": 1
    },
    { # vehicle UI icons for picking up and placing vehicle
        "name": "Placement icon",
        "angles": 1,
        "grid_size": [1,1],
        "subposition_order": [0],
        "sprite_type": "UI",
        "canvas_size": [20,20],
        "camera_world_offset": [0, 0, 0],
        "base_layer_name": 2
    },
    {
        "name": "Straight",
        "sprite_type": "FLAT",
        "symmetric": True
    },
    { # Roads put this here in the order
        "name": "Very Small Curve",
        "sprite_type": "FLAT"
    },
    {
        "name": "T-Intersection",
        "sprite_type": "FLAT"
    },
    {
        "name": "4-Way Intersection",
        "sprite_type": "FLAT",
        "angles": 1
    },
    {
        "name": "Small Curve",
        "sprite_type": "FLAT",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "camera_world_offset": [1, -0.5, 0]
    },
    {
        "name": "Small Curve Gentle Slope Up",
        "sprite_type": "SLOPE",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "camera_world_offset": [1, -0.5, 0],
        "base_layer_name": 6
    },
    {
        "name": "Small Curve Gentle Slope Down",
        "sprite_type": "SLOPE",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "camera_world_offset": [1, -0.5, 0],
        "base_layer_name": 6
    },
    {
        "name": "Small Curve Steep Slope Up",
        "sprite_type": "SLOPE",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "camera_world_offset": [1, -0.5, 0],
        "base_layer_name": 6
    },
    {
        "name": "Small Curve Steep Slope Down",
        "sprite_type": "SLOPE",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "camera_world_offset": [1, -0.5, 0],
        "base_layer_name": 6
    },
    {
        "name": "Medium Curve",
        "sprite_type": "FLAT",
        "grid_size": [3,3],
        "subposition_order": [6,3,4,1,2],
        "camera_world_offset": [1.5, -1, 0]
    },
    {
        "name": "Gentle Slope",
        "sprite_type": "SLOPE",
        "grid_size": [1,2],
        "subposition_order": [1,0],
        "camera_world_offset": [1, 0, 0],
        "base_layer_name": 6
    },
    {
        "name": "Steep Slope",
        "sprite_type": "SLOPE",
        "base_layer_name": 6
    },
    {
        "name": "Diagonal Curve",
        "sprite_type": "FLAT",
        "render_mirror": True,
        "grid_size": [2,3],
        "subposition_order": [4,2,3,0,1],
        "camera_world_offset": [1.5, -0.5, 0]
    },
    {
        "name": "Diagonal Straight",
        "symmetric": True,
        "sprite_type": "FLAT",
        "grid_size": [2,2],
        "subposition_order": [2,0,3,1],
        "camera_world_offset": [0.5, -.5, 0]
    },
    {
        "name": "S-Bend",
        "sprite_type": "FLAT",
        "symmetric": True,
        "render_mirror": True,
        "grid_size": [2,3],
        "subposition_order": [5, 3, 2, 0],
        "camera_world_offset": [1.5, 0.5, 0]
    },
    { # Railways put it here in the order
        "name": "Very Small Curve",
        "sprite_type": "FLAT"
    }
]

for i in range(len(track_piece_manifest)):
    track_piece_manifest[i] = TrackPieceManifest(track_piece_manifest[i], i)