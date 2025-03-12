'''
Copyright (c) 2024 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from mathutils import Vector
from enum import Enum
from typing import List

class SubComponent(Enum):
    FRONT = 0
    BACK = 1
    BODY = 2

def get_vehicle_y_offset():
    additional_offsets = {
        "RAIL":0,
        "ROAD":0,
        "AIR":0,
        "WATER":0,
    }
    return -17 + additional_offsets[bpy.context.scene.loco_graphics_helper_general_properties.transport_mode]

def get_number_of_sprites(object):

    is_bogie = object.loco_graphics_helper_object_properties.object_type == "BOGIE"
    props = object.loco_graphics_helper_vehicle_properties

    if props.null_component:
        return 0

    multiplier = props.number_of_animation_frames
    if props.tilt_angle != 0:
        multiplier = 3
    elif props.braking_lights:
        multiplier = multiplier + 1
    if props.rotational_symmetry:
        multiplier = multiplier / 2

    num_transition_sprites = 0 if is_bogie else 4 + 4
    num_sprites = 0
    if props.sprite_track_flags[0]:
        num_sprites = int(props.flat_viewing_angles) * multiplier
    if props.sprite_track_flags[1]:
        num_sprites = num_sprites + (int(props.sloped_viewing_angles) * 2 + num_transition_sprites) * multiplier
    if props.sprite_track_flags[2]:
        num_sprites = num_sprites + (int(props.sloped_viewing_angles) * 2 + num_transition_sprites) * multiplier
    
    if props.is_airplane:
        num_sprites = num_sprites + int(props.flat_viewing_angles) * multiplier / 2
    return int(num_sprites)

def _get_min_max_axis_bound_box_corners(object, axis):
    bbox_corners = [object.matrix_world * Vector(corner) for corner in object.bound_box]
    min_x = min([x[axis] for x in bbox_corners])
    max_x = max([x[axis] for x in bbox_corners])
    return (min_x, max_x)

def _get_min_max_axis_bound_box_corners_with_children(object, axis):
    mins = []
    maxs = []
    min_x, max_x = _get_min_max_axis_bound_box_corners(object, axis)
    # This can happen if there are no dimensions to this object (or if its 0 width)
    if min_x != max_x:
        mins.append(min_x)
        maxs.append(max_x)

    for c in object.children:
        min_x, max_x = _get_min_max_axis_bound_box_corners_with_children(c, axis)
        if min_x != max_x:
            mins.append(min_x)
            maxs.append(max_x)
    if len(mins) == 0 or len(maxs) == 0:
        return (0, 0)
    
    return (min(mins), max(maxs))

def get_half_width(object):
    body_min_x, body_max_x = _get_min_max_axis_bound_box_corners_with_children(object, 0)
    min_x = object.matrix_world.translation[0] - body_min_x
    max_x = body_max_x - object.matrix_world.translation[0]
    
    return max(min_x, max_x)

class VehicleComponent:
    def __init__(self, car, front, back, body, animations = None):
        self.car = car
        self.front = front
        self.back = back
        self.body = body
        if animations is None:
            self.animations = []
        else:
            self.animations = animations

    def get_object(self, sub_component: SubComponent):
        object_mapping = {
            SubComponent.FRONT.value:self.front,
            SubComponent.BACK.value:self.back,
            SubComponent.BODY.value:self.body,
        }
        return object_mapping[sub_component.value]

    def get_component_index(self, sub_component: SubComponent):
        object = self.get_object(sub_component)
        if object == None:
            return 255
        props = object.loco_graphics_helper_vehicle_properties
        if props.null_component:
            return 255
        return props.index + 128 * props.is_inverted

    def has_sprites(self, sub_component: SubComponent):
        object = self.get_object(sub_component)
        if object is None:
            return False
        props = object.loco_graphics_helper_vehicle_properties
        if props.is_clone:
            return False
        # render_sprites == False does NOT return false here

        if all(v == 0 for v in props.sprite_track_flags):
            return False
        
        return True

    def get_number_of_sprites(self, sub_component: SubComponent):
        object = self.get_object(sub_component)
        return get_number_of_sprites(object)

    def _get_min_max_x_bound_box_corners_with_children(self, object):
        return _get_min_max_axis_bound_box_corners_with_children(object, 0)
    
    def _get_min_max_z_bound_box_corners_with_children(self, object):
        return _get_min_max_axis_bound_box_corners_with_children(object, 2)

    def get_half_width(self):
        mins = []
        maxs = []
        if not self.front is None:
            min_x, max_x = self._get_min_max_x_bound_box_corners_with_children(self.front)
            if min_x != max_x:
                mins.append(min_x)
                maxs.append(max_x)

        if not self.back is None:
            min_x, max_x = self._get_min_max_x_bound_box_corners_with_children(self.back)
            if min_x != max_x:
                mins.append(min_x)
                maxs.append(max_x)
        
        body_min_x, body_max_x = self._get_min_max_x_bound_box_corners_with_children(self.body)
        mins.append(body_min_x)
        maxs.append(body_max_x)
        min_x = self.body.matrix_world.translation[0] - min(mins)
        max_x = max(maxs) - self.body.matrix_world.translation[0]
        
        return max(min_x, max_x)
    
    def get_preferred_body_midpoint(self):
        if self.has_sprites(SubComponent.FRONT) or self.has_sprites(SubComponent.BACK):
            # If it has a real bogey we should put midpoint between the two bogies
            mid_point_x = (self.front.location[0] - self.back.location[0]) / 2 + self.back.location[0]
        else:
            # If it has fake/no bogies we should put midpoint in the centre of the body
            body_min_x, body_max_x = self._get_min_max_x_bound_box_corners_with_children(self.body)
            mid_point_x = (body_min_x + body_max_x) / 2
        return mid_point_x

    def get_bogie_position(self, sub_component: SubComponent):
        assert sub_component != SubComponent.BODY
        body_x = self.body.matrix_world.translation[0]
        half_width = self.get_half_width()
        bounding_box = self.body.loco_graphics_helper_vehicle_properties.bounding_box_override
        if bounding_box:
            body_x = bounding_box.matrix_world.translation[0]
            half_width = get_half_width(bounding_box)
        bogie = self.get_object(sub_component)
        bogie_x = bogie.matrix_world.translation[0]
        position_from_centre = max(body_x, bogie_x) - min(body_x, bogie_x)
        return half_width - position_from_centre

    def get_emitter_x(self):
        if len(self.animations) == 0:
            return None
        x_diff = self.front.matrix_world.translation[0] - self.back.matrix_world.translation[0]
        # print("front_x {} back_x {} anim_x {}".format(self.front.location[0], self.back.location[0], self.animations[0].location[0]))
        x_factor = (1 / x_diff)
        anim_diff = self.front.matrix_world.translation[0] - self.animations[0].matrix_world.translation[0]
        anim_factor = (anim_diff * x_factor) * 128
        return int(anim_factor) + 64

    def get_emitter_z(self):
        if len(self.animations) == 0:
            return None
        target_object = self.front if not self.front is None else self.body
        body_z = target_object.matrix_world.translation[2]
        bounding_box = target_object.loco_graphics_helper_vehicle_properties.bounding_box_override
        if bounding_box:
            body_z = bounding_box.matrix_world.translation[2]
        emitter_z = self.animations[0].matrix_world.translation[2]
        return int((emitter_z - body_z) * 8) + 8 # I don't know if this is steam specific


def get_car_components(cars) -> List[VehicleComponent]:
    components = []
    for car in cars:
        component_bogies = [x for x in car.children if x.loco_graphics_helper_object_properties.object_type == 'BOGIE']
        component_bodies = [x for x in car.children if x.loco_graphics_helper_object_properties.object_type == 'BODY']
        component_animations = [x for x in car.children if x.loco_graphics_helper_object_properties.object_type == 'ANIMATION']

        if len(component_bodies) != 1:
            print("Car {} requires at least one child BODY".format(car.name))
            continue

        if len(component_bogies) != 2:
            components.append(VehicleComponent(car, None, None, component_bodies[0], component_animations))
            continue
        
        front_bogie = component_bogies[0] if component_bogies[0].location[0] > component_bogies[1].location[0] else component_bogies[1]
        back_bogie = component_bogies[1] if component_bogies[0].location[0] > component_bogies[1].location[0] else component_bogies[0]

        components.append(VehicleComponent(car, front_bogie, back_bogie, component_bodies[0], component_animations))
    return components