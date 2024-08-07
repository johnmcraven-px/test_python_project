import pandas as pd

# Load the forces data
forces_df = pd.read_csv('openfoam_case/postProcessing/forces/0/forces.dat', sep='\s+', comment='#', header=None)

# Inspect the first few rows to understand the structure
print(forces_df.head())

# Update the column names based on the structure of your forces.dat file
forces_df.columns = ['Time', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz', 'Tx', 'Ty', 'Tz', 'Vx', 'Vy', 'Vz']

# Extract thrust (assuming it's the force in the x-direction)
thrust = forces_df['Fx']

# Define propeller angular velocity (rad/s)
angular_velocity = 100.0  # Adjust according to your simulation setup

# Convert the torque column to numeric, forcing errors to NaN
torque = pd.to_numeric(forces_df['Mx'], errors='coerce')

# Replace NaN values with 0 (or handle them as needed)
torque.fillna(0, inplace=True)

# Calculate power (Power = Torque * Angular Velocity)
power = torque * angular_velocity

# Save results to a CSV file
results_df = pd.DataFrame({'Time': forces_df['Time'], 'Thrust': thrust, 'Power': power})
results_df.to_csv('thrust_power.csv', index=False)

print("Thrust and power data saved to thrust_power.csv")
