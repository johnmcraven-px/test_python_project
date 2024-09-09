import argparse
import json
import os

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Save blade_length and num_blades to a JSON file.")
    
    # Add positional arguments
    parser.add_argument('blade_length', type=float, help='Length of the blade')
    parser.add_argument('num_blades', type=int, help='Number of blades')
    parser.add_argument('air_flow_speed', type=int, help='Air flow speed')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create a dictionary from the arguments
    data = {
        'blade_length': args.blade_length,
        'num_blades': args.num_blades,
        'air_flow_speed': args.air_flow_speed
    }


    os.makedirs("../data/sim_output", exist_ok=True)
    
    # Save the data to a JSON file
    with open('../data/sim_output/simulated.vtk', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print("Data has been saved to simulated.vtk")

if __name__ == "__main__":
    main()