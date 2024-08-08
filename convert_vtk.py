import vtk
import os

# Define the input and output directories
input_dir = "case/VTK"
output_dir = "case/VTK_XML"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate over all .vtk files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".vtk"):
        # Construct the full input file path
        input_file_path = os.path.join(input_dir, filename)
        
        # Read the legacy VTK file
        reader = vtk.vtkUnstructuredGridReader()
        reader.SetFileName(input_file_path)
        reader.Update()
        
        # Extract the file extension to determine the type of XML writer to use
        file_root, file_ext = os.path.splitext(filename)
        
        # Create the appropriate writer based on the data type
        if reader.IsFileUnstructuredGrid():
            writer = vtk.vtkXMLUnstructuredGridWriter()
            output_file_path = os.path.join(output_dir, f"{file_root}.vtu")
        elif reader.IsFilePolyData():
            writer = vtk.vtkXMLPolyDataWriter()
            output_file_path = os.path.join(output_dir, f"{file_root}.vtp")
        else:
            print(f"Unsupported VTK file type: {input_file_path}")
            continue
        
        # Set the input and output file names
        writer.SetInputConnection(reader.GetOutputPort())
        writer.SetFileName(output_file_path)
        
        # Write the XML VTK file
        writer.Write()
        print(f"Converted {input_file_path} to {output_file_path}")

print("Conversion complete.")