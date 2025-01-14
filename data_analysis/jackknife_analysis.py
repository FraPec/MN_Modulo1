import os
import sys
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, load_config, prompt_user_choice
from jackknife_utils import perform_jackknife_blocking

if __name__ == "__main__":
    """
    Main script for Jackknife analysis on lattice metrics.
    """
    # Setup logging
    log_dir = "../logs"
    log_file = "jackknife_analysis.log"
    setup_logging(log_dir=log_dir, log_file=log_file)
    
    try:
        # Load the YAML configuration
        config_path = "../configs/jackknife_config.yaml"
        config = load_config(config_path)

        # Extract settings from the config
        first_index = config['settings']['first_index']
        max_block_size = config['settings']['max_block_size_default']
        num_cores = config['settings']['num_cores_default']
        data_columns = config['settings']['data_columns']
        log_dir = config['paths']['log_dir']
        output_dir = config['paths']['data_dir']
        plot_dir = config['paths']['plot_dir']
        input_paths = config['paths']['default_files']
        
        # Print the loaded configuration
        print("Loaded configuration:")
        for key, value in config.items():
            print(f"{key}: {value}\n")

        # Prompt the user to confirm the configuration
        if not prompt_user_choice("Is this configuration correct?"):
            # Ask for each parameter individually if the configuration is incorrect
            first_index_input = input("Enter first index (default: {}): ".format(first_index)).strip()
            first_index = int(first_index_input) if first_index_input else first_index

            max_block_size_input = input("Enter max block size (default: {}): ".format(max_block_size)).strip()
            max_block_size = int(max_block_size_input) if max_block_size_input else max_block_size

            num_cores_input = input("Enter number of cores (default: {}): ".format(num_cores)).strip()
            num_cores = int(num_cores_input) if num_cores_input else num_cores

            data_columns_input = input("Enter data columns as comma-separated values (default: {}): ".format(','.join(data_columns))).strip()
            data_columns = data_columns_input.split(',') if data_columns_input else data_columns

            log_dir_input = input("Enter log directory (default: {}): ".format(log_dir)).strip()
            log_dir = log_dir_input if log_dir_input else log_dir

            output_dir_input = input("Enter data directory (default: {}): ".format(data_dir)).strip()
            output_dir = data_dir_input if data_dir_input else data_dir

            plot_dir_input = input("Enter plot directory (default: {}): ".format(plot_dir)).strip()
            plot_dir = plot_dir_input if plot_dir_input else plot_dir

            # Optionally select input paths from directories
            input_paths = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")

        
        # Perform analysis with the loaded settings
        perform_jackknife_blocking(input_paths, output_dir, first_index, num_cores, max_block_size)

    except Exception as main_e:
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)
