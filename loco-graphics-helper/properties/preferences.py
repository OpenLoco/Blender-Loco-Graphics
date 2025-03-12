'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from bpy.types import AddonPreferences
from .file_versioning import current_file_version

class RCTGraphicsHelperPreferences(AddonPreferences):
    printable_idname = "loco-graphics-helper"
    bl_idname = printable_idname

    # make sure to add an updater to file_updater.py
    RCTPluginVersion = bpy.props.IntProperty(
        name="RCT Tools Version",
        description="What version of the fork this project is for. Number updates when a backwards-incompatible change is introduced.",
        default=current_file_version)

    # currently unused
    orct2_directory = bpy.props.StringProperty(
        name="OpenRCT2 Path",
        description="The path to OpenRCT2. This should point to the directory that contains the object folder.",
        maxlen=1024,
        subtype='DIR_PATH',
        default="")

    # currently unused
    opengraphics_directory = bpy.props.StringProperty(
        name="OpenGraphics Repository Path",
        description="Root directory for the OpenGraphics repository, if available.",
        maxlen=1024,
        subtype='DIR_PATH',
        default="")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label("""RCT Graphics Helper, "{}" Fork, file version {}""".format(self.bl_idname, self.RCTPluginVersion))
