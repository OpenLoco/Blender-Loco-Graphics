'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy

from ..res.res import get_material_object


# Builder responsible for creating materials necessary for the rendering process
class MaterialsBuilder:

    def __init__(self):
        super().__init__()
        self.prefix = ""
        self.suffix = ""
        return

    def import_materials(self, context):
        self.remove_data(bpy.data.materials,"Recolorable 1")
        self.remove_data(bpy.data.materials,"Recolorable 2")
        self.remove_data(bpy.data.node_groups,"LOCO_EEVEE Phong BSDF")
        self.remove_data(bpy.data.node_groups,"LOCO_EEVEE Recolor AOV")
        self.remove_data(bpy.data.node_groups,"LOCO_EEVEE Position AOV")

        get_material_object("Material","Recolorable 1")
        get_material_object("Material","Recolorable 2", True)
        get_material_object("Material","Lumpy Material", True)
        get_material_object("Material","Matte Material", True)
        get_material_object("Material","Semigloss Material", True)
        get_material_object("Material","Glossy Material", True)

    def remove_data(self, type, name):
        if name in type:
            #type.remove(type[name])
            type[name].name = name + ".old"
