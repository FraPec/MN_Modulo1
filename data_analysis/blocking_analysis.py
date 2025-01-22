import os
import sys
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, prompt_user_choice
from blocking_utils import calculate_blocking_variances, check_existing_blocking_files, process_csv_for_blocking
from plot_utils import plot_blocking_variance
from interface_utils import get_user_inputs_for_blocking_analysis




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
        min_block_size = user_inputs["min_block_size"]
        num_cores = user_inputs["num_cores"]
        
        # Ensure output directories exist
        ensure_directory(output_dir)
        ensure_directory(plot_dir)
        
        plot = prompt_user_choice("Want to plot?")
        # Process each selected path
        for input_path in input_paths:
            if os.path.isdir(input_path):
                # If it's a directory, process all valid files inside
                for csv_file in sorted(os.listdir(input_path)):
                    if csv_file.endswith("_summary.csv"):
                        input_file = os.path.join(input_path, csv_file)
                        process_csv_for_blocking(input_file, output_dir, plot_dir, min_block_size, max_block_size, num_cores, plot=plot)
            elif os.path.isfile(input_path):
                # If it's a single file, process it directly
                process_csv_for_blocking(input_path, output_dir, plot_dir, min_block_size, max_block_size, num_cores, plot=plot)

    except Exception as main_e:
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)
