import numpy as np
import pandas as pd

# Parameters
np.random.seed(42)
n_batches = 20
n_runs_per_batch = 100

# Generate data
data = []
for batch in range(n_batches):
    for run in range(n_runs_per_batch):
        performance = np.random.uniform(0.7, 1.0)
        time_to_complete = np.random.uniform(10, 30)
        constraint_satisfaction = np.random.uniform(0.6, 1.0)
        failure_reason = np.random.choice([None, 'Generation', 'Evaluation'], p=[0.8, 0.15, 0.05])
        pareto_score = performance * constraint_satisfaction / time_to_complete
        data.append([batch + 1, run + 1, performance, time_to_complete, constraint_satisfaction, failure_reason, pareto_score])

df = pd.DataFrame(data, columns=['Batch', 'Run', 'Performance', 'Time', 'ConstraintSatisfaction', 'FailureReason', 'ParetoScore'])

# Save data to CSV for later use in visualizations
df.to_csv('../data/viz_gen/optimization_results_1.csv', index=False)