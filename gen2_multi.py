import numpy as np
import pandas as pd

# Parameters
np.random.seed(42)
n_batches = 20
n_runs_per_batch = 100

# Function to simulate realistic trends and clusters
def generate_batch_data(batch_number):
    data = []
    for run in range(n_runs_per_batch):
        # Introduce trend over batches
        base_performance = 0.7 + (batch_number * 0.01) + np.random.uniform(-0.05, 0.05)
        base_time = 20 + np.random.normal(0, 5)
        base_constraint_satisfaction = 0.8 - (batch_number * 0.01) + np.random.uniform(-0.05, 0.05)

        # Introduce some outliers
        if np.random.rand() < 0.05:
            performance = np.random.uniform(0.5, 0.6)
            time_to_complete = np.random.uniform(30, 40)
            constraint_satisfaction = np.random.uniform(0.5, 0.6)
            failure_reason = np.random.choice(['Generation', 'Evaluation'])
        else:
            performance = base_performance
            time_to_complete = base_time
            constraint_satisfaction = base_constraint_satisfaction
            failure_reason = None if np.random.rand() > 0.1 else np.random.choice(['Generation', 'Evaluation'])
        
        # Introduce clusters in Pareto scores
        if batch_number % 3 == 0:
            pareto_score = performance * constraint_satisfaction / (time_to_complete * 1.2)
        elif batch_number % 5 == 0:
            pareto_score = performance * constraint_satisfaction / (time_to_complete * 0.8)
        else:
            pareto_score = performance * constraint_satisfaction / time_to_complete

        data.append([batch_number + 1, run + 1, performance, time_to_complete, constraint_satisfaction, failure_reason, pareto_score])

    return data

# Generate data for all batches
for batch in range(n_batches):
    batch_data = generate_batch_data(batch)

    # Convert to DataFrame
    df = pd.DataFrame(batch_data, columns=['Batch', 'Run', 'Performance', 'Time', 'ConstraintSatisfaction', 'FailureReason', 'ParetoScore'])

    # Save data to CSV for later use in visualizations
    df.to_csv(f'../data/viz_gen/optimization_results_batch_{batch}.csv', index=False)