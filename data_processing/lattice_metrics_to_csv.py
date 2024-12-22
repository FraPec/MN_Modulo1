import os
import sys
import yaml
import logging
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import (load_config, ensure_directory, load_binary_file, 
                        extract_lattice_side, extract_beta, save_lattice_metrics_to_csv, 
                        setup_logging
                    )
from interface_utils import get_user_inputs_for_saving_lattice_metrics_to_csv



def process_file(file_path, output_dir, idx_threshold = 1000, n_cols=3):
    """
    Process a single binary file to compute required metrics and save them.

    Parameters:
        file_path (str): Path to the input file.
        output_dir (str): Output directory.
        idx_threshold (int): Starting index for analysis (post-thermalization).
        n_cols (int): Number of columns in the binary file.
    """
    logging.info(f"[INFO] Processing file: {file_path}")

    try:
        # Extract metadata from the file name
        lattice_side = extract_lattice_side(file_path)
        beta = extract_beta(file_path)
    
        # Load the binary data
        data = load_binary_file(file_path, n_cols)
        
        # Ensure data has enough rows
        if len(data) <= idx_threshold:
            raise ValueError(f"Insufficient data after index {idx_threshold}.")
        
        mx, my, epsilon = data[idx_threshold:, 0], data[idx_threshold, 1], data[idx_threshold, 2]
        m2 = mx**2 + my**2  # m squared
    
        try:
            mx, my, epsilon = data[idx_threshold:, 0], data[idx_threshold:, 1], data[idx_threshold:, 2]
            m2 = mx**2 + my**2  # m squared
            
            # Calculate metrics
            metrics = {
                "mx": mx,
                "my": my,
                "epsilon": epsilon,
                "absm": np.sqrt(m2),  # norm of vector_m
                "m2": m2,             # m^2
                "m4": m2**2,          # m^4
            }
        except Exception as metric_err:
            raise ValueError(f"Metric calculation error for file {file_path}: {metric_err}")
    

        # Save metrics to a CSV file
        save_lattice_metrics_to_csv(output_dir, lattice_side, beta, metrics)
        logging.info(f"Successfully processed and saved metrics for file: {file_path}")
        
        
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}", exc_info=True)



if __name__ == "__main__":
    """
    Main script for processing binary files to generate summarized CSV outputs.
    """
    
    # Setup logging
    setup_logging(log_dir="../logs", log_file="lattice_metrics_to_csv.log")
    
    logging.info("Starting the lattice metrics processing script.")
    
    # Load configuration
    config_path = "../configs/lattice_metrics_to_csv_config.yaml"
    if not os.path.isfile(config_path):
        logging.error(f"Configuration file not found at {config_path}. Exiting...")
        sys.exit(1)
        
    config = load_config(config_path)
    logging.info(f"Loaded configuration from {config_path}.")

    # Get user inputs for input paths and output directory
    user_inputs = get_user_inputs_for_saving_lattice_metrics_to_csv(config_path)
    input_paths = user_inputs["input_paths"]
    output_dir = user_inputs["output_dir"]
    index_thr_from_termalization = int(user_inputs["index_threshold"])  

    # Validate input paths
    if not input_paths:
        logging.error("No input paths provided. Exiting...")
        sys.exit(1)


    if not os.path.exists(output_dir):
        logging.warning(f"Output directory {output_dir} does not exist. Creating...")
        ensure_directory(output_dir)
    
    # Allow user to select directories and gather all binary files within
    dir_files = []
    for input_path in input_paths:
        if os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                dir_files.extend(os.path.join(root, f) for f in files if f.endswith(".bin"))
        elif os.path.isfile(input_path) and input_path.endswith(".bin"):
            dir_files.append(input_path)

    if not dir_files:
        logging.info("No binary files found. Exiting...")
        sys.exit(0)


    logging.info(f"Found {len(dir_files)} binary files to process.")


    # Process each file
    successful_files = 0
    for i, file_path in enumerate(dir_files):
        try:
            process_file(file_path, output_dir, idx_threshold=index_thr_from_termalization, n_cols=3)
            successful_files += 1
            logging.info(f"Processed {i+1}/{len(dir_files)} files.")
        except Exception as e:
            logging.error(f"Skipping file {file_path} due to an error: {e}")

    logging.info(f"Processing completed. Successfully processed {successful_files}/{len(dir_files)} files.")