import os
import bpy

res_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)))

scenedefaults_path= os.path.join(res_path,"scene.blend")
matdefaults_path= os.path.join(res_path,"materials.blend")
tooldefaults_path= os.path.join(res_path,"")

def get_scene_object(category, name, reuse_local=False):
    full_path = os.path.normpath(os.path.join(scenedefaults_path,category))
    bpy.ops.wm.append(filename = name, directory = full_path, do_reuse_local_id = reuse_local)

def get_scene_files(category, files, reuse_local=False):
    full_path = os.path.normpath(os.path.join(scenedefaults_path,category))
    bpy.ops.wm.append(files = files, directory = full_path, do_reuse_local_id = reuse_local)

def get_material_object(category, name, reuse_local=False):
    full_path = os.path.normpath(os.path.join(matdefaults_path,category))
    result = bpy.ops.wm.append(filename = name, directory = full_path, do_reuse_local_id = reuse_local)

def get_material_files(category, files, reuse_local=False):
    full_path = os.path.normpath(os.path.join(matdefaults_path,category))
    result = bpy.ops.wm.append(files = files, directory = full_path, do_reuse_local_id = reuse_local)

def get_tool_object(category, name, reuse_local=False):
    full_path = os.path.normpath(os.path.join(tooldefaults_path,category))
    bpy.ops.wm.append(filename = name, directory = full_path, do_reuse_local_id = reuse_local)

def get_tool_files(category, files, reuse_local=False):
    full_path = os.path.normpath(os.path.join(tooldefaults_path,category))
    bpy.ops.wm.append(files = files, directory = full_path, do_reuse_local_id = reuse_local)
