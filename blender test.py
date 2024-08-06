import bpy
import math
from mathutils import Matrix

def delete_default_cube():
    bpy.ops.object.select_all(action='DESELECT')
    if "Cube" in bpy.data.objects:
        bpy.data.objects['Cube'].select_set(True)
        bpy.ops.object.delete()

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

def create_center_hub(radius, height):
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, depth=height, location=(0, 0, height / 2))
    hub = bpy.context.object
    hub.name = "PropellerHub"
    
    # Create stainless steel material
    mat = bpy.data.materials.new(name="StainlessSteel")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    # Create material nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set material properties
    bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['IOR'].default_value = 0.6  # Set reflectivity to 0.6
    bsdf.inputs['Roughness'].default_value = 0.1
    
    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to hub
    if hub.data.materials:
        hub.data.materials[0] = mat
    else:
        hub.data.materials.append(mat)
    
    return hub

def create_propeller(num_blades, blade_length, blade_width, blade_height, twist_angle, hub_radius, hub_height, blade_thickness):
    propeller = bpy.data.objects.new("Propeller", None)
    bpy.context.collection.objects.link(propeller)
    
    hub = create_center_hub(hub_radius, hub_height)
    hub.parent = propeller
    
    blades = []
    for i in range(num_blades):
        angle = (2 * math.pi / num_blades) * i
        blade = create_propeller_blade(blade_length, blade_width, blade_height, twist_angle, blade_thickness)
        blade.rotation_euler = (0, 0, angle)
        blade.location = (0, 0, blade_height)  # Align bottom of blade with blade height
        blade.parent = propeller
        blades.append(blade)
    
    return propeller, hub, blades

def create_lightbox():
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -5))
    bottom_plane = bpy.context.object
    bottom_plane.name = "BottomPlane"
    bottom_mat = bpy.data.materials.new(name="BottomMaterial")
    bottom_mat.use_nodes = True
    nodes = bottom_mat.node_tree.nodes
    links = bottom_mat.node_tree.links
    
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    emission = nodes.new(type='ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1, 1, 1, 1)
    emission.inputs['Strength'].default_value = 20  # Increase brightness
    links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    bottom_plane.data.materials.append(bottom_mat)
    
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, -20, 10), rotation=(math.radians(90), 0, 0))
    back_plane = bpy.context.object
    back_plane.name = "BackPlane"
    back_plane.data.materials.append(bottom_mat)
    
    bpy.ops.mesh.primitive_plane_add(size=40, location=(-20, 0, 10), rotation=(0, math.radians(90), 0))
    left_plane = bpy.context.object
    left_plane.name = "LeftPlane"
    left_plane.data.materials.append(bottom_mat)
    
    bpy.ops.mesh.primitive_plane_add(size=40, location=(20, 0, 10), rotation=(0, math.radians(-90), 0))
    right_plane = bpy.context.object
    right_plane.name = "RightPlane"
    right_plane.data.materials.append(bottom_mat)

def render_multiple_views(propeller, filepath_base):
    angles = [(0, -10, 10), (10, -10, 10), (-10, -10, 10), (0, -20, 10)]
    for i, location in enumerate(angles):
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.object
        camera.rotation_euler = (math.radians(60), 0, 0)
        
        # Ensure the camera is pointing at the propeller
        bpy.context.scene.camera = camera
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = propeller
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        
        # Render the image
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = f"{filepath_base}_view{i+1}.png"
        bpy.ops.render.render(write_still=True)

# Parameters for the propeller
num_blades = 4
blade_length = 3.0
blade_width = 0.3
blade_height = 0.1
twist_angle = 30.0
hub_radius = 0.2
hub_height = 0.4
blade_thickness = 0.02

# Define the rotation speed in RPM
rotation_speed = 150

# Delete the default cube
delete_default_cube()

# Create the lightbox
create_lightbox()

# Create the propeller
propeller, hub, blades = create_propeller(num_blades, blade_length, blade_width, blade_height, twist_angle, hub_radius, hub_height, blade_thickness)

# Join the propeller blades and hub into a single mesh for export
bpy.context.view_layer.objects.active = hub
bpy.ops.object.select_all(action='DESELECT')
hub.select_set(True)
for blade in blades:
    blade.select_set(True)
bpy.ops.object.join()

# Export the propeller to STL
filepath_base = "./output/propeller"
bpy.ops.export_mesh.stl(filepath=f"{filepath_base}.stl", use_selection=True)

# Set world background to pure white
bpy.context.scene.world.use_nodes = True
world_nodes = bpy.context.scene.world.node_tree.nodes
world_nodes.clear()
bg_node = world_nodes.new(type='ShaderNodeBackground')
bg_node.inputs['Color'].default_value = (1, 1, 1, 1)
world_output = world_nodes.new(type='ShaderNodeOutputWorld')
bpy.context.scene.world.node_tree.links.new(bg_node.outputs['Background'], world_output.inputs['Surface'])

# Save the Blender file with a fixed name
bpy.ops.wm.save_as_mainfile(filepath=f"{filepath_base}.blend")

# Add lighting for a lightbox effect
bpy.ops.object.light_add(type='AREA', location=(0, -10, 10))
top_light = bpy.context.object
top_light.data.energy = 2000
top_light.data.size = 20

bpy.ops.object.light_add(type='AREA', location=(0, 10, 10))
bottom_light = bpy.context.object
bottom_light.data.energy = 2000
bottom_light.data.size = 20
bottom_light.rotation_euler = (math.radians(180), 0, 0)

bpy.ops.object.light_add(type='AREA', location=(10, 0, 10))
right_light = bpy.context.object
right_light.data.energy = 2000
right_light.data.size = 20
right_light.rotation_euler = (0, math.radians(90), 0)

bpy.ops.object.light_add(type='AREA', location=(-10, 0, 10))
left_light = bpy.context.object
left_light.data.energy = 2000
left_light.data.size = 20
left_light.rotation_euler = (0, math.radians(-90), 0)

# Render multiple views
render_multiple_views(propeller, filepath_base)

# Setup camera for animation
bpy.ops.object.camera_add(location=(0, -10, 10))
camera = bpy.context.object
camera.rotation_euler = (math.radians(60), 0, 0)
bpy.context.scene.camera = camera

# Ensure the camera is pointing at the propeller
constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = propeller
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Animation setup
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = int(25 * 60 / rotation_speed)  # Number of frames to complete one rotation

propeller.rotation_mode = 'XYZ'
propeller.keyframe_insert(data_path="rotation_euler", frame=1)
propeller.rotation_euler = (0, 0, math.radians(360))
propeller.keyframe_insert(data_path="rotation_euler", frame=bpy.context.scene.frame_end)

# Set interpolation mode to linear
for fcurve in propeller.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'LINEAR'

# Hide lightbox planes and cameras in the viewport, but not in rendering
for obj in bpy.data.objects:
    if obj.type in {'LIGHT', 'CAMERA'} or "Plane" in obj.name:
        obj.hide_set(True)
        obj.hide_render = False

# Setup render settings for video
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
bpy.context.scene.render.filepath = f"{filepath_base}_animation.mp4"

# Render the animation
bpy.ops.render.render(animation=True)
