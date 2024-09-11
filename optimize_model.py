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

def fit_minimum_boundary(scatter_data):
    """Fit a curve to the minimum boundary using curve fitting."""
    
    # Define a function that models the boundary as a quadratic curve (as an example)
    def boundary_func(blades_length, a, b, c):
        return a * blades_length**2 + b * blades_length + c

    # Sort the data by blade_length for better fitting
    scatter_data_sorted = scatter_data.sort_values(by='blade_length')

    # Fit the curve using the num_blades as a rough representation of blade effect on minimum
    params, _ = curve_fit(boundary_func, scatter_data_sorted['blade_length'], scatter_data_sorted['metricX'] + scatter_data_sorted['metricY'])

    # Generate fitted values for plotting and output
    fitted_curve = pd.DataFrame({
        'blade_length': scatter_data_sorted['blade_length'],
        'fitted_metric': boundary_func(scatter_data_sorted['blade_length'], *params)
    })

    return fitted_curve, params

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


def calculate_distance_to_curve(scatter_data, fitted_curve):
    """Calculate the distance of each point to the curve."""
    # Merge scatter data and fitted curve on blade_length
    merged_data = pd.merge(scatter_data, fitted_curve, on='blade_length')
    
    # Calculate the distance as sqrt((metricX - fitted_metric)^2 + (metricY - fitted_metric)^2)
    merged_data['distance_to_curve'] = np.sqrt(
        (merged_data['metricX'] - merged_data['fitted_metric'])**2 + 
        (merged_data['metricY'] - merged_data['fitted_metric'])**2
    )
    
    return merged_data

def find_top_10_closest_points(scatter_data, fitted_curve):
    """Find the top 10 points closest to the fitted curve."""
    merged_data = calculate_distance_to_curve(scatter_data, fitted_curve)
    
    # Sort by distance and select the top 10 closest points
    top_10_points = merged_data.nsmallest(10, 'distance_to_curve')
    
    return top_10_points

def output_top_10_points_to_json(top_10_points, output_dir='../data/points_output'):
    """Output the top 10 points to individual JSON files."""
    # Ensure the output directory exists
    
    for _, row in top_10_points.iterrows():
        file_name = f"point_{row['blade_length']:.2f}_{row['num_blades']}.json"
        output_path = os.path.join(output_dir, file_name)
        
        # Prepare the data to save in JSON format
        point_data = {
            'blade_length': row['blade_length'],
            'num_blades': row['num_blades'],
            'metricX': row['metricX'],
            'metricY': row['metricY'],
            'distance_to_curve': row['distance_to_curve']
        }
        
        # Write the JSON file
        with open(output_path, 'w') as json_file:
            json.dump(point_data, json_file, indent=4)
        
        print(f"Point saved to {output_path}")

# def plot_scatter_data(data):
#     """Plot the scatter data using Altair."""
#     scatter_plot = alt.Chart(data).mark_circle(size=60).encode(
#         x='metricX:Q',
#         y='metricY:Q',
#         color='num_blades:O',  # Color by number of blades
#         tooltip=['metricX', 'metricY', 'num_blades', 'blade_length']
#     ).properties(
#         title='MetricX vs MetricY Scatter Plot'
#     )
    
#     return scatter_plot

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

    fitted_curve = fit_minimum_boundary(scatter_data)
    fitted_curve.to_csv("../data/optimize_output/curve.csv", index=False)

    # Step 4: Find the top 10 closest points to the curve
    top_10_points = find_top_10_closest_points(scatter_data, fitted_curve)

    # Step 5: Output each of the top 10 points to individual JSON files
    output_top_10_points_to_json(top_10_points)

    # Step 3: Plot the scatter data
    # scatter_plot = plot_scatter_data(scatter_data)
    # scatter_plot.show()

if __name__ == "__main__":
    main()
