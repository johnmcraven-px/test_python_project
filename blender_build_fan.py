import bpy
import math
from mathutils import Matrix
import sys
import os
import importlib

# Add the directory containing cad_functions.py to sys.path
script_dir = os.path.dirname(os.path.abspath("cad_functions.py"))
sys.path.append(script_dir)
import cad_functions as cadfn
importlib.reload(cadfn)

# Set the output path
output_path = '../data/output'
os.makedirs(output_path, exist_ok=True)

output_file = 'output.blend'
output_file_path = output_path + '/' + output_file

if os.path.exists(output_file_path):
    os.remove(output_file_path)

# Delete the default cube if it exists
if "Cube" in bpy.data.objects:
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()

# Room dimensions and placement
room_length = 5.86
room_width = 4.85
room_height = 2.8
room_center_x = -2.7
room_center_y = 2
wall_thickness = 0.01 # Wall thickness of 1 cm
bottom_z = 0

# Door dimensions and placement to cut out from the walls
door_height = 2.1  # 2.1 m
door_width = 0.768006  # 0.768006 m
door_x = room_center_x + room_length / 2 - wall_thickness/2 # Positioned on the wall at the right end of the room
door_y = room_center_y  # Positioned at y = 2

# Outlet dimensions and placement
outlet_height = 1.05  # 1.05 m
outlet_width = 0.845193  # 0.845193 m
outlet_x = room_center_x - room_length / 2 + wall_thickness/2 # Positioned on the wall at the left end of the room
outlet_y = room_center_y  # Positioned at y = 2
outlet_z = door_height - outlet_height / 2  # Positioned so the top is at the same height as the door

# Create the room
room = cadfn.create_room(room_length, room_width, room_height, room_center_x, room_center_y, bottom_z, wall_thickness)

# Create the door as a cube with 0 thickness
door = cadfn.create_door(door_height, door_width, door_x, door_y, wall_thickness)

# Apply the boolean cut using the duplicate outlet object
door_cutout = cadfn.create_door(door_height, door_width, door_x, door_y, 1.1*wall_thickness)
cadfn.apply_boolean_cut(room, door_cutout)

# Create the outlet as a cube with 0 thickness
outlet = cadfn.create_outlet(outlet_height, outlet_width, outlet_x, outlet_y, outlet_z, wall_thickness)

# Apply the boolean cut using the duplicate outlet object
outlet_cutout = cadfn.create_outlet(outlet_height, outlet_width, outlet_x, outlet_y, outlet_z, 1.1*wall_thickness)
cadfn.apply_boolean_cut(room, outlet_cutout)

# Fan dimensions and placement
fan_center_x = -3
fan_center_y = 2
fan_z = 2.4  # Fan hub height before adjustment
blade_length = 0.7  # 70 cm
blade_width = 0.15  # 15 cm at the widest point
blade_height = 0.15  # 15 cm
blade_thickness = 0.035  # 3.5 cm
hub_radius = 0.15  # 30 cm diameter
hub_height = 0.15  # 10 cm height
twist_angle = 20  # 20 degree twist
number_of_blades = 4 # 4 blades in fan

# Create the fan (hub and blades)
fan_hub = cadfn.create_fan(number_of_blades, blade_length, blade_width, blade_height, blade_thickness, hub_radius, hub_height, twist_angle, fan_center_x, fan_center_y, fan_z)

# Pole dimensions and placement
fan_pole_diameter = 0.03  # 3 cm
fan_pole_height = room_height - fan_z  # From fan to ceiling

# Create the pole
pole = cadfn.create_pole(fan_pole_diameter, fan_pole_height, fan_center_x, fan_center_y, fan_z)

# Join the pole, hub, and blades into a single object called "Fan"
bpy.ops.object.select_all(action='DESELECT')
fan_hub.select_set(True)
pole.select_set(True)
bpy.context.view_layer.objects.active = fan_hub
bpy.ops.object.join()
fan_hub.name = "Fan"

# AMI dimensions and placement
ami_diameter = 1.3 * 2 * blade_length  # Diameter is 1.3 times twice the blade length
ami_height = 0.64  # 0.64 m height
ami_x = fan_center_x  # x position is -3
ami_y = fan_center_y  # y position is 2
ami_z = room_height - ami_height / 2 + 0.01  # z position is room height minus half the AMI height plus 1 cm

# Create the AMI cylinder
ami = cadfn.create_ami(ami_diameter, ami_height, ami_x, ami_y, ami_z)

# Desk dimensions and placement
desk_top_length = 2.34896
desk_top_width = 1.2
desk_top_thickness = 0.1
desk_leg_height = 0.86672
desk_leg_x = 0.15  # 15 cm
desk_leg_y = 0.05  # 5 cm
desk_z = 0.84172  # The top of the desk

# Create the desk as a single object
desk = cadfn.create_desk(desk_top_length, desk_top_width, desk_top_thickness, desk_leg_height, desk_leg_x, desk_leg_y, desk_z, fan_center_x, fan_center_y)

# Save the Blender file
bpy.ops.wm.save_as_mainfile(filepath=output_file_path)

cadfn.export_stl('Room', f'{output_path}/room.stl')
cadfn.export_stl('Desk_Top', f'{output_path}/desk.stl')
cadfn.export_stl('Fan', f'{output_path}/fan.stl')
cadfn.export_stl('Door', f'{output_path}/door.stl')
cadfn.export_stl('Outlet', f'{output_path}/outlet.stl')
cadfn.export_stl('AMI', f'{output_path}/AMI.stl')

