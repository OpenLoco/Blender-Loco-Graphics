'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from ..res.res import get_scene_object

# Builder for populating the scene with objects


class SceneBuilder:

    def __init__(self):
        self.prefix = ""
        self.suffix = ""
        return

    def build(self, context):
        scene = context.scene

        self.remove_data(bpy.data.scenes,"LOCO_EEVEE")
        self.remove_data(bpy.data.node_groups,"LOCO_EEVEE Compositor")
        self.remove_data(bpy.data.worlds, "LOCO_EEVEE World")

        self.remove_scene_object(context, "Camera")
        self.remove_scene_object(context, "Light")

        has_tile_size_reference = "Tile Size Reference" in scene.objects

        self.remove_scene_object(context, "Tile Size Reference")
        self.remove_scene_object_recursive(context, "Rig")
        self.remove_collection(context, "LightCameraRig")

        get_scene_object("Scene", "LOCO_EEVEE")
        new_scene = bpy.data.scenes["LOCO_EEVEE"]

        self.move_data_to_new_scene(context, scene, new_scene)

        context.window.scene = new_scene
        context.window.view_layer = new_scene.view_layers[0]

        bpy.data.scenes.remove(scene, do_unlink=True)

    def remove_data(self, type, name):
        if name in type:
            #type.remove(type[name])
            type[name].name = name + ".old"

    def remove_scene_object(self, context, name):
        if name in context.scene.objects:
            bpy.data.objects.remove(
                context.scene.objects[name], do_unlink=True)

    def remove_scene_object_recursive(self, context, name):
        if name in context.scene.objects:
            children_recursive = context.scene.objects[name].children_recursive
            for child in children_recursive:
                bpy.data.objects.remove(child, do_unlink = True)

            bpy.data.objects.remove(context.scene.objects[name], do_unlink = True)

    def remove_collection(self, context, name):
        if name in bpy.data.collections:
            children_recursive = bpy.data.collections[name].children_recursive
            for child in children_recursive:
                bpy.data.objects.remove(child, do_unlink=True)
            bpy.data.collections.remove(bpy.data.collections[name], do_unlink=True)

    def move_data_to_new_scene(self, context, old_scene, new_scene):
        for object in old_scene.collection.objects:
            new_scene.collection.objects.link(object)
        for collection in old_scene.collection.children:
            new_scene.collection.children.link(collection)
