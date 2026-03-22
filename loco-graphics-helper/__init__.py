'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import traceback

from .register_classes import register_classes, unregister_classes
from . import developer_utils
import importlib
import bpy

plugin_name = "Locomotion Eevee Render Tool"

bl_info = {
    "name": "Locomotion Eevee Render Tool",
    "description": "Render tool to replicate Locomotion graphics (based on RCT Graphics Helper)",
    "author": "Olivier Wervers & OpenLoco Team",
    "version": (0, 2, 1),
    "blender": (4, 3, 2),
    "location": "Render",
    "support": "COMMUNITY",
    "category": "Render"}

# load and reload submodules
##################################

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(
    __path__, __name__, "bpy" in locals())


# register
##################################

def register():

    register_classes()

    print("Registered {} with {} modules".format(
        plugin_name, len(modules)))


def unregister():

    unregister_classes()

    print("Unregistered {}".format(plugin_name))
