import trimesh
import numpy as np

# Helper function to save models
def save_model(mesh, filename):
    mesh.export(filename)
    print(f'Saved: {filename}')

# Generate parameterized models
def generate_twisted_torus(param1, param2):
    angle = np.linspace(0, 2 * np.pi, 50)
    x = (param1 + 0.3 * np.cos(param2 * angle)) * np.cos(angle)
    y = (param1 + 0.3 * np.cos(param2 * angle)) * np.sin(angle)
    z = 0.3 * np.sin(param2 * angle)
    vertices = np.vstack((x, y, z)).T
    faces = trimesh.geometry.faces_from_edges(trimesh.graph.edges_as_tuples(trimesh.graph.nx.cycle_graph(len(vertices))))
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_helix(param1, param2):
    t = np.linspace(0, param2 * np.pi, 100)
    x = param1 * np.cos(t)
    y = param1 * np.sin(t)
    z = t / param2
    vertices = np.vstack((x, y, z)).T
    faces = trimesh.geometry.faces_from_edges(trimesh.graph.edges_as_tuples(trimesh.graph.nx.path_graph(len(vertices))))
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_star_shape(param1, param2):
    angle = np.linspace(0, 2 * np.pi, int(param2), endpoint=False)
    radii = np.array([param1, 0.5 * param1] * int(param2 / 2))
    x = radii * np.cos(angle)
    y = radii * np.sin(angle)
    z = np.zeros_like(x)
    vertices = np.vstack((x, y, z)).T
    faces = trimesh.geometry.faces_from_edges(trimesh.graph.edges_as_tuples(trimesh.graph.nx.cycle_graph(len(vertices))))
    return trimesh.Trimesh(vertices=vertices, faces=faces)

# Parameters to vary
param_values = [(1.0, 3.0), (1.5, 5.0), (2.0, 7.0), (1.0, 8.0), (1.5, 10.0)]

# Generate and save models
for i, (param1, param2) in enumerate(param_values):
    twisted_torus = generate_twisted_torus(param1, param2)
    save_model(twisted_torus, f'twisted_torus_p1-{param1}_p2-{param2}.gltf')

    helix = generate_helix(param1, param2)
    save_model(helix, f'helix_p1-{param1}_p2-{param2}.gltf')

    star_shape = generate_star_shape(param1, param2)
    save_model(star_shape, f'star_shape_p1-{param1}_p2-{param2}.gltf')

print("All models have been generated and saved.")