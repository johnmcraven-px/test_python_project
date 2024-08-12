import bpy
import sys

# Ensure the blend file is provided as an argument
if len(sys.argv) < 5:
    print("Usage: blender --background --python script.py -- <blend_file_path> <output_file_path>")
    sys.exit(1)

# Get the file paths from the arguments
blend_file_path = sys.argv[sys.argv.index("--") + 1]
output_file_path = sys.argv[sys.argv.index("--") + 2]

# Open the .blend file
bpy.ops.wm.open_mainfile(filepath=blend_file_path)

# Function to extract object information
def extract_mesh_details(obj):
    mesh = obj.data
    vertices = [v.co[:] for v in mesh.vertices]
    edges = [e.vertices[:] for e in mesh.edges]
    faces = [f.vertices[:] for f in mesh.polygons]
    return {
        'name': obj.name,
        'type': obj.type,
        'vertices': vertices,
        'edges': edges,
        'faces': faces,
        'location': obj.location[:],
        'rotation': obj.rotation_euler[:],
        'scale': obj.scale[:]
    }

# Collect detailed information
mesh_info = []

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mesh_details = extract_mesh_details(obj)
        mesh_info.append(mesh_details)

# Output details to a text file
output_path = output_file_path
with open(output_path, 'w') as file:
    for obj in mesh_info:
        file.write(f"Object Name: {obj['name']}\n")
        file.write(f"  Type: {obj['type']}\n")
        file.write(f"  Location: {obj['location']}\n")
        file.write(f"  Rotation: {obj['rotation']}\n")
        file.write(f"  Scale: {obj['scale']}\n")
        file.write("  Vertices:\n")
        for v in obj['vertices']:
            file.write(f"    {v}\n")
        file.write("  Edges:\n")
        for e in obj['edges']:
            file.write(f"    {e}\n")
        file.write("  Faces:\n")
        for f in obj['faces']:
            file.write(f"    {f}\n")
        file.write("\n")

print(f"Object information has been saved to {output_file_path}")
