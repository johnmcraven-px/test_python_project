import bpy
import math
from mathutils import Matrix

# Set the output path
output_path = './output/geometry_new'

# Delete the default cube if it exists
if "Cube" in bpy.data.objects:
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()

# Create the room with the given dimensions and placement
def create_room(length, width, height, center_x, center_y, bottom_z, wall_thickness):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(center_x, center_y, bottom_z + height/2))
    room_cube = bpy.context.object
    room_cube.scale = (length, width, height)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(center_x, center_y, bottom_z + height/2))
    room_inner = bpy.context.object
    room_inner.scale = ((length - 2 * wall_thickness), (width - 2 * wall_thickness), (height - 2 * wall_thickness))
    
    mod_bool = room_cube.modifiers.new(type="BOOLEAN", name="Boolean")
    mod_bool.operation = 'DIFFERENCE'
    mod_bool.object = room_inner
    bpy.context.view_layer.objects.active = room_cube
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    bpy.data.objects.remove(room_inner)


    room_cube.name = "Room"
    return room_cube

# Create the desk with correctly positioned rectangular legs
def create_desk(top_length, top_width, top_thickness, leg_height, leg_x, leg_y, desk_z, room_center_x, room_center_y):
    # Create desk top
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(room_center_x, room_center_y, desk_z + top_thickness/2)
    )
    desk_top = bpy.context.object
    desk_top.scale = (top_length, top_width, top_thickness)
    desk_top.name = "Desk_Top"
    
    # Add rectangular legs at each corner
    legs = []
    leg_positions = [(-top_length/2 + leg_x/2, -top_width/2 + leg_y/2),
                     (-top_length/2 + leg_x/2, top_width/2 - leg_y/2),
                     (top_length/2 - leg_x/2, -top_width/2 + leg_y/2),
                     (top_length/2 - leg_x/2, top_width/2 - leg_y/2)]
    
    for pos in leg_positions:
        bpy.ops.mesh.primitive_cube_add(
            size=1, 
            location=(room_center_x + pos[0], room_center_y + pos[1], leg_height/2)
        )
        leg = bpy.context.object
        leg.scale = (leg_x, leg_y, leg_height)
        leg.name = f'Desk_Leg_{len(legs) + 1}'
        legs.append(leg)
    
    # Join the desk top and legs into a single object
    bpy.ops.object.select_all(action='DESELECT')
    desk_top.select_set(True)
    for leg in legs:
        leg.select_set(True)
    bpy.context.view_layer.objects.active = desk_top
    bpy.ops.object.join()
    
    return desk_top

# Function to create a propeller blade with a curved profile
def create_propeller_blade(length, width, height, twist_angle, thickness):
    mesh = bpy.data.meshes.new(name="PropellerBlade")
    obj = bpy.data.objects.new(name="PropellerBlade", object_data=mesh)
    bpy.context.collection.objects.link(obj)
    
    # Create a more realistic blade shape with a curved profile and thickness
    verts = [
        (0, -width / 2, 0),
        (0, width / 2, 0),
        (length * 0.7, width / 4, height / 2),
        (length * 0.7, -width / 4, height / 2),
        (length, width / 8, height),
        (length, -width / 8, height),
        (0, -width / 2, -thickness),
        (0, width / 2, -thickness),
        (length * 0.7, width / 4, height / 2 - thickness),
        (length * 0.7, -width / 4, height / 2 - thickness),
        (length, width / 8, height - thickness),
        (length, -width / 8, height - thickness)
    ]
    
    faces = [
        (0, 1, 2, 3),
        (2, 3, 5, 4),
        (0, 1, 7, 6),
        (6, 7, 9, 8),
        (8, 9, 11, 10),
        (4, 5, 11, 10),
        (0, 3, 9, 6),
        (1, 2, 8, 7)
    ]
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Apply twist to the blade
    angle_rad = math.radians(twist_angle)
    twist_matrix = Matrix.Rotation(angle_rad, 4, 'X')
    
    for vertex in obj.data.vertices:
        vertex.co = twist_matrix @ vertex.co
    
    # Create carbon fiber material
    mat = bpy.data.materials.new(name="CarbonFiber")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Create material nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set material properties
    bsdf.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1)  # Darker color for carbon fiber
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['IOR'].default_value = 0.6  # Set reflectivity to 0.6
    bsdf.inputs['Roughness'].default_value = 0.2
    
    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to blade
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return obj

# Function to create the fan with 4 blades and a central hub
def create_fan(num_blades, blade_length, blade_width, blade_height, blade_thickness, hub_radius, hub_height, twist_angle, fan_center_x, fan_center_y, fan_z):
    # Move the hub down by half the hub height
    hub_z = fan_z + hub_height / 5
    bpy.ops.mesh.primitive_cylinder_add(radius=hub_radius, depth=hub_height, location=(fan_center_x, fan_center_y, hub_z))
    hub = bpy.context.object
    hub.name = "Fan_Hub"
    
    # Create blades and attach them to the hub
    blades = []
    for i in range(num_blades):
        blade = create_propeller_blade(blade_length, blade_width, blade_height, twist_angle, blade_thickness)
        blade.rotation_euler = (0, 0, i * (2 * math.pi / num_blades))
        blade.location = (fan_center_x, fan_center_y, fan_z)
        blade.select_set(True)
        blades.append(blade)
    
    # Join the blades and hub into a single object
    bpy.ops.object.select_all(action='DESELECT')
    hub.select_set(True)
    for blade in blades:
        blade.select_set(True)
    bpy.context.view_layer.objects.active = hub
    bpy.ops.object.join()
    
    return hub

# Function to create the pole
def create_pole(diameter, height, center_x, center_y, bottom_z):
    bpy.ops.mesh.primitive_cylinder_add(radius=diameter/2, depth=height, location=(center_x, center_y, bottom_z + height/2))
    pole = bpy.context.object
    pole.name = "Fan_Pole"
    return pole

# Function to create the door
def create_door(height, width, x_position, y_position, thickness):
    z_position = height / 2  # The door's z position should be half its height
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_position, y_position, z_position))
    door = bpy.context.object
    door.scale = (thickness, width, height)  # Thickness is 0 (x scale is 0)
    door.name = "Door"
    return door

# Function to create the outlet
def create_outlet(height, width, x_position, y_position, z_position, thickness):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_position, y_position, z_position))
    outlet = bpy.context.object
    outlet.scale = (thickness, width, height)  # Thickness is 0 (x scale is 0)
    outlet.name = "Outlet"
    return outlet

# Function to create the AMI cylinder
def create_ami(diameter, height, x_position, y_position, z_position):
    bpy.ops.mesh.primitive_cylinder_add(radius=diameter / 2, depth=height, location=(x_position, y_position, z_position))
    ami = bpy.context.object
    ami.name = "AMI"
    return ami

# Apply a boolean difference to cut out the door and outlet from the room
def apply_boolean_cut(room_obj, cutout_obj):
    mod_bool = room_obj.modifiers.new(type="BOOLEAN", name="Boolean")
    mod_bool.operation = 'DIFFERENCE'
    mod_bool.object = cutout_obj
    bpy.context.view_layer.objects.active = room_obj
    bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.data.objects.remove(cutout_obj, do_unlink=True)


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
room = create_room(room_length, room_width, room_height, room_center_x, room_center_y, bottom_z, wall_thickness)

# Create the door as a cube with 0 thickness
door = create_door(door_height, door_width, door_x, door_y, wall_thickness)

# Apply the boolean cut using the duplicate outlet object
door_cutout = create_door(door_height, door_width, door_x, door_y, 1.1*wall_thickness)
apply_boolean_cut(room, door_cutout)

# Create the outlet as a cube with 0 thickness
outlet = create_outlet(outlet_height, outlet_width, outlet_x, outlet_y, outlet_z, wall_thickness)

# Apply the boolean cut using the duplicate outlet object
outlet_cutout = create_outlet(outlet_height, outlet_width, outlet_x, outlet_y, outlet_z, 1.1*wall_thickness)
apply_boolean_cut(room, outlet_cutout)

# Fan dimensions and placement
fan_center_x = -3
fan_center_y = 2
fan_z = 2.4  # Fan hub height before adjustment
blade_length = 0.6  # 60 cm
blade_width = 0.15  # 15 cm at the widest point
blade_height = 0.15  # 15 cm
blade_thickness = 0.02  # 2 cm
hub_radius = 0.15  # 30 cm diameter
hub_height = 0.15  # 10 cm height
twist_angle = 20  # 20 degree twist

# Create the fan (hub and blades)
fan_hub = create_fan(4, blade_length, blade_width, blade_height, blade_thickness, hub_radius, hub_height, twist_angle, fan_center_x, fan_center_y, fan_z)

# Desk dimensions and placement
desk_top_length = 2.34896
desk_top_width = 1.2
desk_top_thickness = 0.1
desk_leg_height = 0.86672
desk_leg_x = 0.15  # 15 cm
desk_leg_y = 0.05  # 5 cm
desk_z = 0.84172  # The top of the desk

# Create the desk as a single object
desk = create_desk(desk_top_length, desk_top_width, desk_top_thickness, desk_leg_height, desk_leg_x, desk_leg_y, desk_z, fan_center_x, fan_center_y)

# Pole dimensions and placement
fan_pole_diameter = 0.03  # 3 cm
fan_pole_height = room_height - fan_z  # From fan to ceiling

# Create the pole
pole = create_pole(fan_pole_diameter, fan_pole_height, fan_center_x, fan_center_y, fan_z)

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
ami = create_ami(ami_diameter, ami_height, ami_x, ami_y, ami_z)

# Save the Blender file
bpy.ops.wm.save_as_mainfile(filepath=f'{output_path}/output.blend')

# Export each object to its respective STL file
def export_stl(obj_name, filepath):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select_set(True)
    bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True, global_scale=1)

export_stl('Room', f'{output_path}/room.stl')
export_stl('Desk_Top', f'{output_path}/desk.stl')
export_stl('Fan', f'{output_path}/fan.stl')
export_stl('Door', f'{output_path}/door.stl')
export_stl('Outlet', f'{output_path}/outlet.stl')
export_stl('AMI', f'{output_path}/AMI.stl')

