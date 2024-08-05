import trimesh
import numpy as np

# Helper function to save models
def save_model(mesh, filename):
    fName = f'../data/shapes/{filename}'
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

# Function to create a circle mesh
def create_circle(radius=1.0, segments=16):
    theta = np.linspace(0, 2 * np.pi, segments, endpoint=False)
    vertices = np.column_stack((np.cos(theta) * radius, np.sin(theta) * radius, np.zeros_like(theta)))
    faces = np.column_stack((np.arange(segments), np.roll(np.arange(segments), -1), np.full(segments, segments)))
    vertices = np.vstack((vertices, np.array([0, 0, 0])))
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def generate_helix(radius, turns, tube_radius=0.1):
    # Create a helix
    t = np.linspace(0, turns * np.pi, 100)
    x = radius * np.cos(t)
    y = radius * np.sin(t)
    z = t / turns
    points = np.vstack((x, y, z)).T
    
    # Create circular cross-sections along the helix path
    path = trimesh.load_path(points)
    circles = [create_circle(radius=tube_radius) for _ in points]
    for i, (circle, point) in enumerate(zip(circles, points)):
        # Move the circles to the correct location along the path
        circle.apply_translation(point)
        if i > 0:
            # Rotate the circle to align with the path
            prev_point = points[i - 1]
            tangent = point - prev_point
            tangent /= np.linalg.norm(tangent)
            rotation_matrix = trimesh.geometry.align_vectors([0, 0, 1], tangent)
            circle.apply_transform(rotation_matrix)
    
    # Sweep the circles along the path to create a tube
    tube = trimesh.util.concatenate([circles[i] for i in range(len(circles))])
    
    return tube

def generate_star_shape(radius, points):
    # Ensure points is an even number for correct pairing
    points = int(points // 2) * 2
    
    # Create a star shape
    angle = np.linspace(0, 2 * np.pi, points, endpoint=False)
    radii = np.array([radius, 0.5 * radius] * (points // 2))
    x = radii * np.cos(angle)
    y = radii * np.sin(angle)
    z = np.zeros_like(x)
    vertices = np.vstack((x, y, z)).T
    
    # Generate faces from vertices
    faces = [[i, (i+1) % len(vertices), len(vertices)] for i in range(len(vertices))]
    vertices = np.vstack([vertices, np.array([0, 0, 0])])  # Add center vertex
    star = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    return star

# Parameters to vary
param_values = [(1.0, 0.3, 3.0), (1.5, 0.5, 5.0), (2.0, 0.4, 7.0), (1.0, 0.3, 8.0), (1.5, 0.5, 10.0)]

# Generate and save models
for i, (param1, param2, param3) in enumerate(param_values):
    twisted_torus = generate_twisted_torus(param1, param2, param3)
    save_model(twisted_torus, f'twisted_torus_p1-{param1}_p2-{param2}_p3-{param3}.glb')

    helix = generate_helix(param1, param3)
    save_model(helix, f'helix_p1-{param1}_p2-{param3}.glb')

    star_shape = generate_star_shape(param1, param3)
    save_model(star_shape, f'star_shape_p1-{param1}_p2-{param3}.glb')

print("All models have been generated and saved.")