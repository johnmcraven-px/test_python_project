import json
import random
import numpy as np
import pandas as pd
import altair as alt
import os

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
        rad = random.uniform(0, np.pi / 2.0)
        constant_error = 2.0 / num_files_used

        xerr = random.uniform(0, 0.1)
        yerr = random.uniform(0, 0.1)

        metricX = .1 + (1 - np.sin(rad)) * 0.9 + xerr + constant_error
        metricY = .1 + (1 - np.cos(rad)) * 0.9 + xerr + constant_error

        # Append the generated point to the data
        data.append({
            'num_blades': num_blades,
            'blade_length': blade_length,
            'metricX': metricX,
            'metricY': metricY
        })

    return pd.DataFrame(data)

def pareto_front_data():
    """Generate the Pareto front for the quarter-circle region."""
    # The Pareto front is a quarter circle from (1, 0) to (0, 1)
    rad = np.linspace(0, np.pi / 2, 100)
    
    pareto_data = pd.DataFrame({
        'metricX': .1 + (1 - np.sin(rad)) * 0.9,  # x-coordinates of Pareto front
        'metricY': .1 + (1 - np.cos(rad)) * 0.9   # y-coordinates of Pareto front
    })
    
    return pareto_data


def find_top_10_closest_points(data):
    """Find the top 10 points closest to the Pareto front."""
    # The Pareto front is a quarter circle with metricX^2 + metricY^2 = constant
    # We calculate the distance from each point to the Pareto front curve
    pareto_curve = plot_pareto_front().data

    # Calculate distance to the Pareto front for each point in data
    data['distance_to_pareto'] = np.sqrt(
        (data['metricX'] - pareto_curve['metricX'].values[:, None])**2 +
        (data['metricY'] - pareto_curve['metricY'].values[:, None])**2
    ).min(axis=0)
    
    # Sort by distance and select the top 10 closest points
    top_10_points = data.nsmallest(10, 'distance_to_pareto')
    
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

    pareto_data = pareto_front_data()
    pareto_data.to_csv("../data/optimize_output/curve.csv", index=False)

    # Step 4: Find the top 10 closest points to the Pareto frontier
    top_10_points = find_top_10_closest_points_to_pareto(scatter_data, pareto_data)

    # Step 5: Output each of the top 10 points to individual JSON files
    output_top_10_points_to_json(top_10_points)


if __name__ == "__main__":
    main()
