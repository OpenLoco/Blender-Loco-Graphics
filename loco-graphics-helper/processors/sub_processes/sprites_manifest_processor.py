'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import json
import os
from collections import OrderedDict

from .sub_processor import SubProcessor

# Processor for populating the sprites manifest.


class SpritesManifestProcessor(SubProcessor):
    def __init__(self, renderer):
        super().__init__()

        self.renderer = renderer

    def applicable(self, master_context):
        return True

    def process(self, master_context, callback=None):
        task = master_context.task
        file_path = os.path.join(
            task.get_output_folder(), "sprites.json")

        def frame_filter(a):
            return a.index >= 0 and a.offset_x >= -128 and a.offset_x <= 127 and a.offset_y >= -128 and a.offset_y < 127

        output_info_list = [a for a in task.output_info if frame_filter(a)]

        def get_index(output_info):
            return output_info.index

        output_info_list.sort(key=get_index)
        
        images = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as images_file:
                    images = json.loads(images_file.read(),
                                        object_pairs_hook=OrderedDict)
                    images_file.close()
            except Exception as e:
                print("Error when reading sprites.json",e)

        with open(file_path, "w") as images_file:
            for output_info in output_info_list:
                while len(images) <= output_info.index:
                    images.append({})

                image_dict = OrderedDict()
                image_dict["path"] = "sprites/" + \
                    os.path.basename(output_info.path)
                image_dict["x"] = output_info.offset_x
                image_dict["y"] = output_info.offset_y
                if output_info.flags != 0:
                    image_dict["flags"] = output_info.flags
                if output_info.zoomOffset != 0:
                    image_dict["zoomSprite"] = output_info.zoomSprite

                images[output_info.index] = image_dict

            images_file.write(json.dumps(images, indent=4))
            images_file.close()
