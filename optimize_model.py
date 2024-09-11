import json
import random
import numpy as np
import pandas as pd
import altair as alt
import os
from scipy.spatial import ConvexHull

def read_model_json(json_file):
    """Read the model JSON and return num_files_used."""
    with open(json_file, 'r') as file:
        model_data = json.load(file)
        return model_data.get('num_files_used', 1)  # Default to 1 if missing

def generate_scatter_data(num_files_used, num_points=100):
    """Generate scatter data with metricX and metricY based on num_blades and blade_length."""
    
    # The optimal values for num_blades and blade_length where metricX^2 + metricY^2 is minimized
    optimal_num_blades = 4
    optimal_blade_length = 0.45

    data = []

    for _ in range(num_points):
        # Generate random num_blades and blade_length
        num_blades = random.randint(2, 7)
        blade_length = random.uniform(0.2, 0.7)

        # Compute the "distance" from the optimal point
        delta_blades = num_blades - optimal_num_blades
        delta_blade_length = blade_length - optimal_blade_length

        # Use some predictable function to map to metricX and metricY
        # We use sine and cosine here with the deltas to simulate variation
        metricX = abs(delta_blades * np.cos(blade_length * np.pi)) + 0.5
        metricY = abs(delta_blade_length * np.sin(num_blades * np.pi / 3)) + 0.5

        # Add some noise based on the number of files used (more files = less noise)
        noise_factor = 1.0 / np.sqrt(num_files_used)
        metricX += random.uniform(-0.1, 0.1) * noise_factor
        metricY += random.uniform(-0.1, 0.1) * noise_factor

        # Ensure values stay within reasonable bounds (e.g., don't hit zero)
        metricX = max(0.1, metricX)
        metricY = max(0.1, metricY)

        # Append the generated point to the data
        data.append({
            'num_blades': num_blades,
            'blade_length': blade_length,
            'metricX': metricX,
            'metricY': metricY
        })

    return pd.DataFrame(data)


def find_pareto_frontier(scatter_data):
    """Find the Pareto frontier using the Convex Hull algorithm."""
    # Select only metricX and metricY columns for fitting the Pareto frontier
    points = scatter_data[['metricX', 'metricY']].values

    # Compute the Convex Hull, which includes the Pareto frontier
    hull = ConvexHull(points)

    # Extract the points that form the Pareto frontier
    pareto_points = scatter_data.iloc[hull.vertices].sort_values(by='metricX')
    
    return pareto_points


def write_pareto_frontier_to_csv(pareto_frontier):
    """Write Pareto frontier data to a CSV file."""
    pareto_frontier.to_csv("../data/optimize_output/curve.csv", index=False)
    print(f"Pareto frontier data has been written to ../data/optimize_output/curve.csv")

def calculate_distance_to_pareto(scatter_data, pareto_frontier):
    """Calculate the distance of each point to the Pareto frontier."""
    scatter_data['distance_to_pareto'] = np.inf  # Start with large distances

    # Calculate the minimum distance to the Pareto frontier for each point
    for i, row in scatter_data.iterrows():
        scatter_data.at[i, 'distance_to_pareto'] = np.min(np.sqrt(
            (pareto_frontier['metricX'] - row['metricX'])**2 +
            (pareto_frontier['metricY'] - row['metricY'])**2
        ))
    
    return scatter_data

def find_top_10_closest_points_to_pareto(scatter_data, pareto_frontier):
    """Find the top 10 points closest to the Pareto frontier."""
    scatter_data_with_distances = calculate_distance_to_pareto(scatter_data, pareto_frontier)
    
    # Sort by distance and select the top 10 closest points
    top_10_points = scatter_data_with_distances.nsmallest(10, 'distance_to_pareto')
    
    return top_10_points

def output_top_10_points_to_json(top_10_points, output_dir='../data/points_output'):
    """Output the top 10 points to individual JSON files."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    for _, row in top_10_points.iterrows():
        file_name = f"point_{row['blade_length']:.2f}_{row['num_blades']}.json"
        output_path = os.path.join(output_dir, file_name)
        
        # Prepare the data to save in JSON format
        point_data = {
            'blade_length': row['blade_length'],
            'num_blades': row['num_blades'],
            'metricX': row['metricX'],
            'metricY': row['metricY'],
            'distance_to_pareto': row['distance_to_pareto']
        }
        
        # Write the JSON file
        with open(output_path, 'w') as json_file:
            json.dump(point_data, json_file, indent=4)
        
        print(f"Point saved to {output_path}")

def main():

    os.makedirs("../data/optimize_output", exist_ok=True)
    os.makedirs("../data/points_output", exist_ok=True)
    # Step 1: Read num_files_used from the model.json
    json_file = '../data/model_output/model.json'  # Path to the model.json
    num_files_used = read_model_json(json_file)
    print(f"Number of files used: {num_files_used}")

    # Step 2: Generate the scatter data
    scatter_data = generate_scatter_data(num_files_used)
    scatter_data.to_csv("../data/optimize_output/scatter.csv", index=False)

    pareto_frontier = find_pareto_frontier(scatter_data)
    # Step 3: Write the Pareto frontier to a separate CSV
    write_pareto_frontier_to_csv(pareto_frontier)

    # Step 4: Find the top 10 closest points to the Pareto frontier
    top_10_points = find_top_10_closest_points_to_pareto(scatter_data, pareto_frontier)

    # Step 5: Output each of the top 10 points to individual JSON files
    output_top_10_points_to_json(top_10_points)


if __name__ == "__main__":
    main()
