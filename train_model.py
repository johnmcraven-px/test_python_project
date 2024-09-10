import os
import re
import json
import random
import csv

def find_files(directory, pattern):
    # Find all files that match the pattern
    vtk_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if re.match(pattern, file):
                vtk_files.append(os.path.join(root, file))
    return vtk_files

def generate_model_json(num_files, output_file):
    # Dummy model information
    model_data = {
        'model_name': 'DummyNet',
        'num_epochs': 10,
        'validation_accuracy': 0.75 + (num_files * 0.02),  # More files, slightly higher accuracy
        'train_loss': 0.5 - (num_files * 0.03),  # More files, lower loss
        'num_files_used': num_files,
        'model_architecture': 'Simple Linear Model',
    }
    
    # Save the dummy model as JSON
    with open(output_file, 'w') as json_file:
        json.dump(model_data, json_file, indent=4)
    
    print(f"Dummy model saved to {output_file}")

def generate_training_csv(num_files, output_file):
    # Simulate training data with slight randomization, converging more if there are more files
    num_epochs = 50
    loss = 1.0
    # accuracy = 0.5
    training_data = []
    
    for epoch in range(1, num_epochs + 1):
        # More files = better convergence, so reduce noise if more files are found
        loss_noise = random.uniform(0.002, 0.01) / (num_files + 1)
        # accuracy_noise = random.uniform(0.01, 0.03) / (num_files + 1)
        
        # Simulate loss decreasing and accuracy increasing as epochs go on
        loss -= 0.02 - loss_noise
        # accuracy += 0.05 + accuracy_noise
        
        # Ensure loss and accuracy stay within bounds
        loss = max(loss, 0.01)
        # accuracy = min(accuracy, 1.0)
        
        training_data.append([epoch, loss])
    
    # Write the data to CSV
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Epoch', 'Loss'])
        writer.writerows(training_data)
    
    print(f"Training data saved to {output_file}")

def main():
    # Directory to search for files
    directory = '../data'
    pattern = r'simulated_.+\.vtk'
    
    # Step 1: Find all matching files
    vtk_files = find_files(directory, pattern)
    num_files = len(vtk_files)
    print(f"Found {num_files} files.")

    os.makedirs("../data/model_output", exist_ok=True)
    
    # Step 2: Generate a dummy model JSON
    model_output_file = '../data/model_output/model.json'
    generate_model_json(num_files, model_output_file)
    
    # Step 3: Generate training data CSV(s)
    training_csv_file = '../data/model_output/training_data.csv'
    generate_training_csv(num_files, training_csv_file)

if __name__ == "__main__":
    main()