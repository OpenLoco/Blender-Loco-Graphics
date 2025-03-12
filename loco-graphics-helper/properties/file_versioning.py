'''
Copyright (c) 2024 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from bpy.app.handlers import persistent

# Updating a project file to a newer version

# each function updates the file to the version in the name
# if only new features were added, use pass argument for an empty function

current_file_version = 6

def getAllComponents():
    return [x for x in bpy.context.scene.objects if x.loco_graphics_helper_object_properties.object_type != 'NONE']
    
class FileVersionUpdater:
    # plugin version 0.1.6
    def version0():
        pass

    # plugin version 0.1.7
    # move component index from 1-index to 0-index
    def version1():
        for object in getAllComponents():
            object.loco_graphics_helper_vehicle_properties.index -= 1

    # plugin version 0.1.8
    # rename roll_angle to tilt_angle
    def version2():
        for object in getAllComponents():
            if "roll_angle" in object.loco_graphics_helper_vehicle_properties:
                object.loco_graphics_helper_vehicle_properties.tilt_angle = object.loco_graphics_helper_vehicle_properties["roll_angle"]

    # plugin version 0.1.9
    # add null component boolean
    def version3():
        for object in getAllComponents():
            if object.loco_graphics_helper_vehicle_properties.index >= 255:
                object.loco_graphics_helper_vehicle_properties.null_component = True
    
    # plugin version 0.1.10
    # add specific Y-offsets per entity type
    def version4():
        bpy.context.scene.loco_graphics_helper_general_properties.y_offset += 17
    
    # plugin version 0.2.0
    # add track rendering
    def version5():
       pass

    # plugin version 0.2.1
    # remove TRACK_LAYER object type
    def version6():
       pass

update_functions = [getattr(FileVersionUpdater, func) for func in dir(FileVersionUpdater) if callable(getattr(FileVersionUpdater, func)) and not func.startswith("__")]

def apply_update():
    print("loco-graphics-helper: Applying updates to file")
    general_properties = bpy.context.scene.loco_graphics_helper_general_properties
    addon_prefs = bpy.context.user_preferences.addons["loco-graphics-helper"].preferences
    assert len(update_functions) == bpy.context.user_preferences.addons["loco-graphics-helper"].preferences.RCTPluginVersion + 1
    for i in range(int(general_properties.RCTPluginVersion)+1, int(addon_prefs.RCTPluginVersion)+1):
        update_functions[i]()
        general_properties.RCTPluginVersion = i
    general_properties.RCTPluginName = addon_prefs.printable_idname

@persistent
def check_for_update(_=None):
    print("loco-graphics-helper: Checking for update")
    general_properties = bpy.context.scene.loco_graphics_helper_general_properties
    addon_prefs = bpy.context.user_preferences.addons["loco-graphics-helper"].preferences
    if general_properties.RCTPluginName != addon_prefs.printable_idname:
        return
    if int(general_properties.RCTPluginVersion) >= int(addon_prefs.RCTPluginVersion):
        return
    print("File version is {}, plugin version is {}".format(general_properties.RCTPluginVersion, addon_prefs.RCTPluginVersion))
    apply_update()

def register_file_updater():
    bpy.app.handlers.load_post.append(check_for_update)

def unregister_file_updater():
    bpy.app.handlers.load_post.remove(check_for_update)
