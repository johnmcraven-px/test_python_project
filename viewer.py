import pyvista as pv

# Path to the VTK file generated by foamToVTK
vtk_file_path = "./openfoam_case/VTK/case_0.vtk"

# Read the VTK file
mesh = pv.read(vtk_file_path)

# Plot the mesh
plotter = pv.Plotter()
plotter.add_mesh(mesh, show_edges=True, color="white")
plotter.show()