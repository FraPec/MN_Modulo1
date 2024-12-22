import os
import sys
import re
import pandas as pd
import numpy as np
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import load_config, ensure_directory, setup_logging
from interface_utils import get_user_inputs_for_principal_quantities_means




def compute_means_from_csv(input_dir, output_dir, output_file, csv_header, header_mapping):
    """
    Process CSV files in subdirectories to compute column-wise means and save results,
    allowing user-specified headers with mapping from input to output headers.

    Parameters:
        input_dir (str): Directory containing subdirectories with CSV files.
        output_dir (str): Directory to save the summary CSV.
        output_file (str): Name of the summary CSV file.
        csv_header (list): List of headers to include in the summary CSV.
        header_mapping (dict): Mapping of input headers to output headers.
    """
    logging.info(f"Processing CSV files in directory: {input_dir}")
    ensure_directory(output_dir)

    summary_data = []

    # Get list of subdirectories and sort them by lattice side (numerical order)
    subdirs = [
        os.path.join(input_dir, d)
        for d in os.listdir(input_dir)
        if os.path.isdir(os.path.join(input_dir, d)) and re.match(r"L\d+", d)
    ]
    subdirs.sort(key=lambda x: int(re.search(r"L(\d+)", x).group(1)))  # Extract lattice side and sort numerically

    # Traverse sorted subdirectories
    for subdir in subdirs:
        logging.info(f"Processing subdirectory: {subdir}")
        for file in sorted(os.listdir(subdir)):
            if file.endswith(".csv"):
                file_path = os.path.join(subdir, file)
                logging.info(f"Processing file: {file_path}")

                # Read CSV file
                try:
                    df = pd.read_csv(file_path)
                    logging.debug(f"Data from {file_path}:\n{df.head()}")  # Log data structure for debugging

                    # Prepare data for the configured header
                    file_data = {}
                    for output_col in csv_header:
                        input_col = header_mapping.get(output_col, output_col)  # Map output column to input column
                        if input_col in df.columns:
                            if output_col in ["L", "beta"]:  # Directly copy values for L and beta
                                file_data[output_col] = df[input_col].iloc[0]
                            else:  # Compute the mean for other columns
                                file_data[output_col] = df[input_col].mean()
                        else:
                            logging.warning(f"Column '{input_col}' not found in {file_path}, using NaN.")
                            file_data[output_col] = np.nan

                    # Append the processed data
                    summary_data.append(file_data)

                except Exception as e:
                    logging.error(f"Failed to process file {file_path}: {e}")

    # Convert the collected data to a DataFrame
    summary_df = pd.DataFrame(summary_data, columns=csv_header)
    logging.debug(f"Final Summary DataFrame:\n{summary_df.head()}")  # Log the final summary for debugging

    # Save the summary to the output file
    summary_output_path = os.path.join(output_dir, output_file)
    try:
        summary_df.to_csv(summary_output_path, index=False)
        logging.info(f"Summary saved to {summary_output_path}")
    except Exception as e:
        logging.error(f"Failed to save summary CSV: {e}")    
    
    
if __name__ == "__main__":
    """
    Main script for summarizing lattice CSV files into a single output file.
    """
    # Configure logging
    log_dir = "../logs"
    log_file = "lattice_means_to_csv.log"
    setup_logging(log_dir=log_dir, log_file=log_file)

    # Load configuration
    config_path = "../configs/lattices_means_to_csv_config.yaml"
    config = load_config(config_path)

    # Get user inputs
    user_inputs = get_user_inputs_for_principal_quantities_means(config_path)
    input_dir = user_inputs["input_dir"]
    output_dir = user_inputs["output_dir"]
    output_file = user_inputs["output_file"]

    # Extract settings
    csv_header = config["settings"]["csv_output_header"]
    header_mapping = config["settings"]["header_mapping"]

    # Compute means and save summary
    try:
        compute_means_from_csv(input_dir, output_dir, output_file, csv_header, header_mapping)
    except Exception as e:
        logging.error(f"Error during computation: {e}")