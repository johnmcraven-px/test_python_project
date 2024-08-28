import bpy
import math
from mathutils import Matrix

# Create the room with the given dimensions and placement
def create_room(length, width, height, center_x, center_y, bottom_z, wall_thickness):
    # print("create_room function called")
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

# Export each object to its respective STL file
def export_stl(obj_name, filepath):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select_set(True)
    bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True, global_scale=1)