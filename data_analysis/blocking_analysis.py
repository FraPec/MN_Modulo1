import os
import sys
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging
from blocking_utils import calculate_blocking_variances
from plot_utils import plot_blocking_variance
from interface_utils import get_user_inputs_for_blocking_analysis


def process_csv_for_blocking(input_file, output_dir, plot_dir, max_block_size, num_cores):
    """
    Process a single CSV file to apply blocking analysis and save results.

    Parameters:
        input_file (str): Path to the input CSV file.
        output_dir (str): Directory to save blocking results.
        plot_dir (str): Directory to save blocking plots.
        max_block_size (int): Maximum block size for the analysis.
        num_cores (int): Number of CPU cores to use for parallel processing.

    Returns:
        None
    """
    logging.info(f"Processing CSV file: {input_file}")
    
    # Read the input file
    try:
        data = pd.read_csv(input_file)
    except Exception as e:
        logging.error(f"Failed to read CSV file {input_file}: {e}")
        return

    # Extract lattice and beta from the file name
    lattice_side = data["L"].iloc[0]
    beta = data["beta"].iloc[0]

    # Prepare output directories
    lattice_csv_dir = os.path.join(output_dir, f"L{lattice_side}")
    ensure_directory(lattice_csv_dir)

    lattice_plot_dir = os.path.join(plot_dir, f"L{lattice_side}")
    ensure_directory(lattice_plot_dir)

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    file_plot_dir = os.path.join(lattice_plot_dir, base_name)
    ensure_directory(file_plot_dir)

    # Prepare results storage
    results = {"block_size": range(1, max_block_size + 1)}

    # Process each column for blocking analysis
    columns_to_process = ["mx", "my", "epsilon", "absm", "m2", "m4"]
    for column in columns_to_process:
        if column not in data.columns:
            logging.warning(f"Column '{column}' not found in {input_file}. Skipping...")
            continue
        
        column_data = data[column].to_numpy()
        logging.info(f"Performing blocking analysis for column: {column}")

        try:
            variances = calculate_blocking_variances(column_data, max_block_size, num_cores)
            results[f"var_{column}"] = list(variances.values())

            # Generate plot
            plot_file = os.path.join(file_plot_dir, f"L{lattice_side}_beta{beta}_{column}_blocking.png")
            plot_blocking_variance(
                variances=variances,
                save_path=plot_file,
                title=f"Blocking Analysis for {column} (L={lattice_side}, β={beta})"
            )
            logging.info(f"Plot saved: {plot_file}")
        except Exception as e:
            logging.error(f"Error during blocking analysis for {column}: {e}")
            continue

    # Save results to CSV
    results_df = pd.DataFrame(results)
    output_file = os.path.join(lattice_csv_dir, f"{base_name}_blocking_results.csv")
    results_df.to_csv(output_file, index=False)
    logging.info(f"Blocking results saved to: {output_file}")
    
    


if __name__ == "__main__":
    """
    Main script for blocking analysis on lattice metrics.
    """
    # Setup logging
    log_dir = "../logs"
    log_file = "blocking_analysis.log"
    setup_logging(log_dir=log_dir, log_file=log_file)

    try:
        # Get user inputs
        config_path = "../configs/blocking_config.yaml"
        user_inputs = get_user_inputs_for_blocking_analysis(config_path)

        # Inputs from user interface
        input_paths = user_inputs["input_paths"]  # Files or directories selected via the interface
        output_dir = user_inputs["data_dir"]  # Directory to save CSV results
        plot_dir = user_inputs["plot_dir"]  # Directory to save plots
        max_block_size = user_inputs["max_block_size"]
        num_cores = user_inputs["num_cores"]

        # Ensure output directories exist
        ensure_directory(output_dir)
        ensure_directory(plot_dir)

        # Process each selected path
        for input_path in input_paths:
            if os.path.isdir(input_path):
                # If it's a directory, process all valid files inside
                for csv_file in sorted(os.listdir(input_path)):
                    if csv_file.endswith("_summary.csv"):
                        input_file = os.path.join(input_path, csv_file)
                        try:
                            logging.info(f"Processing file: {input_file}")
                            process_csv_for_blocking(input_file, output_dir, plot_dir, max_block_size, num_cores)
                        except Exception as e:
                            logging.error(f"Error processing file {input_file}: {e}", exc_info=True)
            elif os.path.isfile(input_path):
                # If it's a single file, process it directly
                try:
                    logging.info(f"Processing file: {input_path}")
                    process_csv_for_blocking(input_path, output_dir, plot_dir, max_block_size, num_cores)
                except Exception as e:
                    logging.error(f"Error processing file {input_path}: {e}", exc_info=True)

    except Exception as main_e:
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)