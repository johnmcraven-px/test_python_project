import vtk
import os
from pygltflib import GLTF2

# Define the input and output directories
input_dir = "../data/case/VTK"
output_dir = "../data/case/VTK_GLB"


# input_dir = "/Users/jmcraven/Documents/prototype_test/vtk/"
# output_dir = "/Users/jmcraven/Documents/prototype_test/vtk_glb/"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def convert_vtk_to_glb(input_filename, output_file_root):
    # Read the legacy VTK file
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(input_filename)
    reader.Update()

    # Get the unstructured grid data
    vtk_data = reader.GetOutput()

    # Convert unstructured grid to polydata
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputData(vtk_data)
    geometry_filter.Update()

    polydata = geometry_filter.GetOutput()

    # Apply any necessary transformations or cleanups
    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputData(polydata)
    clean_filter.Update()

    cleaned_polydata = clean_filter.GetOutput()

    # Create a mapper and actor for the polydata
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(cleaned_polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Set up the GLTF exporter
    gltf_writer = vtk.vtkGLTFExporter()
    gltf_writer.SetFileName(f"{output_file_root}.gltf")
    gltf_writer.SetRenderWindow(render_window)
    gltf_writer.Write()

    # Convert GLTF to GLB
    gltf = GLTF2().load(f"{output_file_root}.gltf")
    gltf.save(f"{output_file_root}.glb")

    print(f"File converted and saved to {output_file_root}")

# Iterate over all .vtk files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".vtk"):
        # Construct the full input file path
        input_file_path = os.path.join(input_dir, filename)
        
        # Extract the file extension to determine the type of XML writer to use
        file_root, file_ext = os.path.splitext(filename)
        
        output_file_path = os.path.join(output_dir, file_root)
        convert_vtk_to_glb(input_file_path, output_file_path)

print("Conversion complete.")