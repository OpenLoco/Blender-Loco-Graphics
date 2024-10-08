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
from ..builders.compositor_builder import CompositorBuilder


class Init(bpy.types.Operator):
    bl_idname = "render.loco_init"
    bl_label = "Initialize Loco graphics helper"

    scene = None
    props = None

    def execute(self, context):
        # Setup render settings
        context.scene.render.resolution_x = 128
        context.scene.render.resolution_y = 128
        context.scene.render.resolution_percentage = 100

        # Output
        context.scene.render.image_settings.color_depth = "8"
        context.scene.render.image_settings.compression = 0
        context.scene.render.image_settings.color_mode = "RGBA"
        context.scene.render.alpha_mode = "TRANSPARENT"

        # Anti-aliasing
        context.scene.render.use_antialiasing = True
        context.scene.render.pixel_filter_type = "BOX"
        context.scene.render.antialiasing_samples = "5"
        context.scene.render.filter_size = 1.4

        # Create render layers
        editor_layer = self.create_render_layer(context, "Editor")
        editor_layer.layers = (True, False, False, True, True, True, True, True,
                               True, True, True, True, True, True, True, True, True, True, True, True)
        editor_layer.layers_zmask = (True, False, False, False, False, False, False, False,
                                     False, False, False, False, False, False, False, False, False, False, False, False)
        editor_layer.use = True

        braking_lights_layer = self.create_render_layer(context, "Braking Lights")
        braking_lights_layer.layers = (False, True, False, False, False, False, False, False,
                                   False, False, False, False, False, False, False, False, False, False, False, False)
        braking_lights_layer.layers_zmask = (True, True, True, True, True, True, True, True, True,
                                         True, False, False, False, False, False, False, False, False, False, False)
        braking_lights_layer.use = False

        braking_lights_layer = self.create_render_layer(context, "Top Down Shadow")
        braking_lights_layer.layers = (False, False, True, False, False, False, False, False,
                                   False, False, False, False, False, False, False, False, False, False, False, False)
        braking_lights_layer.layers_zmask = (False, False, True, False, False, False, False, False, False,
                                         False, False, False, False, False, False, False, False, False, False, False)
        braking_lights_layer.use = False

        self.delete_default_render_layer(context)

        # Create dependencies in the context

        # Materials used in scene builder so do this first
        materialsBuilder = MaterialsBuilder()
        materialsBuilder.build(context)

        sceneBuilder = SceneBuilder()
        sceneBuilder.build(context)

        compositorBuilder = CompositorBuilder()
        compositorBuilder.build(context)

        return {'FINISHED'}

    def delete_default_render_layer(self, context):
        layer = context.scene.render.layers.get("RenderLayer")

        if layer != None:
            context.scene.render.layers.remove(layer)

    def create_render_layer(self, context, name):
        old_layer = context.scene.render.layers.get(name)

        if old_layer != None:
            context.scene.render.layers.remove(old_layer)

        layer = context.scene.render.layers.new(name)

        layer.use_pass_combined = True
        layer.use_pass_material_index = True
        layer.use_pass_object_index = True
        layer.use_zmask = True

        return layer
