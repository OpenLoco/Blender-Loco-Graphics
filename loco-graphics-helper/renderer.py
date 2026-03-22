'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import faulthandler
import os
import threading
import bpy

from .palette_manager import PaletteManager


def get_compositing_node_group(scene):
    return scene.compositing_node_group if bpy.app.version >= (5, 0, 0) else scene.node_tree

def set_output_path(node, base, path, frame_number):
    if bpy.app.version >= (5, 0, 0):
        node.directory = base
        node.file_name = path + "{:04d}".format(frame_number)
    else:
        node.base_path = base+"/"+path

def find_material_by_name(material_name):
    for mat in bpy.data.materials:
        if mat.name == material_name:
            return mat
    return None


def find_node_by_label(tree, node_to_find):
    return None if node_to_find not in tree.nodes else tree.nodes[node_to_find]

# Model for controlling the render settings, and starting render processes


class Renderer:
    def __init__(self, context, palette_manager):
        self.context = context

        self.magick_path = "magick"
        self.floyd_steinberg_diffusion = 5

        self.palette_manager = palette_manager

        self.rendering = False
        self.timer = None
        self.render_finished_callback = None

        camera = context.scene.camera.data

        self.lens_shift_y_offset = round(camera.shift_y *
                                         context.scene.render.resolution_x)

        self.started_with_anti_aliasing = context.scene.render.filter_size > 0.1

        bpy.app.handlers.render_complete.append(self._render_finished)
        bpy.app.handlers.render_cancel.append(self._render_reset)

    # Render out the current scene
    def render(self, output_still, callback):
        self.render_finished_callback = callback

        self._render_started()

        bpy.ops.render.render(write_still=output_still)  # "INVOKE_DEFAULT"

    def _render_started(self):
        if self.rendering:
            return

        print("Starting render...")
        self.rendering = True

    def _render_finished(self, _):
        if not self.rendering:
            return

        print("Finished rendering")

        # Start a timer before calling the callback as the render operator takes a bit to fully finish
        #self.timer = threading.Timer(0.01, self._render_finished_safe)
        # self.timer.start()

        print("Reset renderer")
        self._render_reset()
        print("Call callback")
        if self.render_finished_callback != None:
            self.render_finished_callback()

    def _render_reset(self, _=None):
        if not self.rendering:
            return

        self.rendering = False

        self.set_aa(self.started_with_anti_aliasing)
        self.set_aa_with_background(False)
        self.set_override_material(None)
        self.set_layer("Editor")

    def _render_finished_safe(self):
        self.timer.cancel()

        callback = self.render_finished_callback

        self._render_reset()
        if callback != None:
            callback()

    def get_palette_path(self, palette):
        palette.prepare(self)
        return palette.path

    # Enabled or disables anti-aliasing for the next render
    def set_aa(self, aa):
        pass
        #self.context.scene.render.use_antialiasing = aa

    # Enabled or disables anti-aliasing with the background
    def set_aa_with_background(self, aa_with_background):
        aa_with_backgound_mix_node = find_node_by_label(
            get_compositing_node_group(self.context.scene), "aa_with_background_switch")

        if aa_with_backgound_mix_node is None:
            raise Exception(
                "The compositing node tree does not contain a mix node for anti-aliasing with the background.")

        if aa_with_background:
            aa_with_backgound_mix_node.outputs[0].default_value = 1
        else:
            aa_with_backgound_mix_node.outputs[0].default_value = 0

    # Sets the global override material that the scene is rendered with
    def set_override_material(self, material):
        pass
        """self.context.scene.render.layers["Editor"].material_override = material
        self.context.scene.render.layers["Braking Lights"].material_override = material
        self.context.scene.render.layers["Top Down Shadow"].material_override = material"""

    def set_multi_tile_size(self, width, length):
        width_node = None
        length_node = None
        for key, value in self.context.scene.node_tree.nodes.items():
            if value.label == "width":
                width_node = value
                value.outputs[0].default_value = width
            if value.label == "length":
                length_node = value
                value.outputs[0].default_value = length
        if width_node is None:
            raise Exception("Width composite node could not be found, please click repair")
        if length_node is None:
            raise Exception("Length composite node could not be found, please click repair")

    # Sets the active render layer
    def set_layer(self, layer_name):
        pass
        """layers = ["Editor", "Braking Lights", "Top Down Shadow"]

        for layer in layers:
            self.context.scene.render.layers[layer].use = False
        self.context.scene.render.layers[layer_name].use = True

        input_layer_node = find_node_by_label(
            get_compositing_node_group(self.context.scene), "input_layer")

        if input_layer_node == None:
            raise Exception(
                "The compositing node tree does not contain an input layer node.")

        input_layer_node.layer = layer_name"""

    def set_animation_frame(self, animation_frame_index):
        self.context.scene.frame_set(animation_frame_index)

    def set_cast_shadows(self, cast_shadows):
        self.context.scene.eevee.use_shadows = cast_shadows

    # Sets the still render output path
    def set_output_path(self, path):
        self.context.scene.render.filepath = path

    # Sets the meta (material and tile mask) render output path
    def set_meta_output_path(self, base, path, frame_number):
        # Find the file output node in the compositor to set the output file name and path
        material_index_output_node = find_node_by_label(
            get_compositing_node_group(self.context.scene), "meta_output")

        if material_index_output_node == None:
            raise Exception(
                "The compositing node tree does not contain an output node for the material index.")
        set_output_path(material_index_output_node, base, path, frame_number)
