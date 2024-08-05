import trimesh
import numpy as np
import sys
import os

baseDir = '../data/shapes/'
# Helper function to save models
def save_model(mesh, filename):
    if not os.path.exists(baseDir):
        os.makedirs(baseDir)
    fName = f'{baseDir}{filename}'
    mesh.export(fName)
    print(f'Saved: {fName}')

# Generate parameterized models
def generate_twisted_torus(major_radius, minor_radius, twist):
    # Generate torus mesh
    torus = trimesh.creation.torus(major_radius=major_radius, minor_radius=minor_radius)
    
    # Apply twist
    vertices = torus.vertices.copy()
    angle = np.linspace(0, twist * np.pi, len(vertices))
    vertices[:, 2] += np.sin(angle) * 0.3
    torus.vertices = vertices
    
    return torus


# # Parameters to vary
# param_values = [(1.0, 0.3, 3.0), (1.5, 0.5, 5.0), (2.0, 0.4, 7.0), (1.0, 0.3, 8.0), (1.5, 0.5, 10.0)]

# # Generate and save models
# for i, (param1, param2, param3) in enumerate(param_values):
#     print("xyzTest", param1, param2, param3)
#     twisted_torus = generate_twisted_torus(param1, param2, param3)
#     save_model(twisted_torus, f'twisted_torus_p1-{param1}_p2-{param2}_p3-{param3}.glb')

print("All models have been generated and saved.")


if len(sys.argv) != 4:
    print("Usage: python generate.py p1 p2 p3")
    sys.exit(1)

param1 = float(sys.argv[1])
param2 = float(sys.argv[2])
param3 = float(sys.argv[3])

twisted_torus = generate_twisted_torus(param1, param2, param3)
save_model(twisted_torus, f'twisted_torus_p1-{param1}_p2-{param2}_p3-{param3}.glb')