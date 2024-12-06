import os
import pandas as pd
import yaml
import numpy as np

# Function to safely evaluate strings and convert NumPy objects to native Python types
def safe_eval_and_convert(value):
    try:
        result = eval(value, {"np": np})
        # Convert NumPy objects to native Python types
        if isinstance(result, list):
            return [float(x) for x in result]  # Convert to Python float
        return float(result) if isinstance(result, np.generic) else result
    except Exception:
        return value  # Return as-is if evaluation fails

# Load the CSV file
file_path = "design_results_250.csv"  # Replace with your CSV file path
csv_data = pd.read_csv(file_path)

# Check the number of rows in the CSV
num_rows = csv_data.shape[0]
print(f"Number of rows in CSV: {num_rows}")

# Prepare the YAML structure
yaml_data = {
    "F": "Newton",
    "R": ["cm", "cm", "Newton"],
    "implementations": {}
}

# Populate implementations
for index, row in csv_data.iterrows():
    model_key = f"model{index}"  # Use a unique string key for each model
    yaml_data["implementations"][model_key] = {
        "f_max": [f"{float(row['Max Radius'])} Newton"],  # Add unit N to Max Radius
        "r_min": [f"{float(row['Pulley Sum'])} cm", f"{float(row['Linkage Sum'])} cm", "50 Newton"],  # Add unit cm to Pulley Sum and Linkage Sum
    }

# Define the output directory and file path
output_directory = "gripper_system.mcdplib/gripper_catalogue"
os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist
output_file = os.path.join(output_directory, "gripper_catalogue.yaml")

# Save the YAML data to the specified path
with open(output_file, "w") as yaml_file:
    yaml.dump(yaml_data, yaml_file, default_flow_style=False)

print(f"Modified YAML file with {len(yaml_data['implementations'])} implementations has been created: {output_file}")
