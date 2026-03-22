'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from ..builders.materials_builder import MaterialsBuilder
from ..builders.scene_builder import SceneBuilder

class Init(bpy.types.Operator):
    bl_idname = "loco_eevee.initialize"
    bl_label = "Initialize Loco graphics helper"

    scene = None
    props = None

    def execute(self, context):
        # Materials used in scene builder so do this first
        materialsBuilder = MaterialsBuilder()
        materialsBuilder.import_materials(context)

        sceneBuilder = SceneBuilder()
        sceneBuilder.build(context)

        return {'FINISHED'}
