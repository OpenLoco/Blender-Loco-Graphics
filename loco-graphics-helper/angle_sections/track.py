'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

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
