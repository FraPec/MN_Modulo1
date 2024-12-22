import os
import sys
import yaml
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import load_config, ensure_directory, load_binary_file, extract_lattice_side, extract_beta, save_lattice_metrics_to_csv
from interface_utils import get_user_inputs_for_saving_lattice_metrics_to_csv



def process_file(file_path, output_dir, n_cols=3):
    """
    Process a single binary file to compute required metrics and save them.

    Parameters:
        file_path (str): Path to the input file.
        output_dir (str): Output directory.
        n_cols (int): Number of columns in the binary file.
    """
    print(f"[INFO] Processing file: {file_path}")

    # Extract metadata from the file name
    lattice_side = extract_lattice_side(file_path)
    beta = extract_beta(file_path)

    # Load the binary data
    data = load_binary_file(file_path, n_cols)
    
    mx, my, epsilon = data[:, 0], data[:, 1], data[:, 2]
    m2 = mx**2 + my**2  # m squared

    # Calculate metrics
    metrics = {
        "mx": mx,
        "my": my,
        "epsilon": epsilon,
        "absm": np.sqrt(m2),  # norm of |vector_m|
        "m2": m2,             # m^2
        "m4": m2**2,          # m^4
    }

    # Save metrics to a CSV file
    save_lattice_metrics_to_csv(output_dir, lattice_side, beta, metrics)



if __name__ == "__main__":
    """
    Main script for processing binary files to generate summarized CSV outputs.
    """
    # Load configuration
    config_path = "../configs/lattice_metrics_to_csv_config.yaml"
    config = load_config(config_path)

    # Get user inputs for input paths and output directory
    user_inputs = get_user_inputs_for_saving_lattice_metrics_to_csv(config_path)
    input_paths = user_inputs["input_paths"]
    output_dir = user_inputs["output_dir"]

    # Allow user to select directories and gather all binary files within
    dir_files = []
    for input_path in input_paths:
        if os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                dir_files.extend(os.path.join(root, f) for f in files if f.endswith(".bin"))
        else:
            dir_files.append(input_path)

    # Ensure the output directory exists
    ensure_directory(output_dir)

    # Process each file in the collected paths
    for file_path in dir_files:
        try:
            process_file(file_path, output_dir)
        except Exception as e:
            print(f"[ERROR] Error processing {file_path}: {e}")