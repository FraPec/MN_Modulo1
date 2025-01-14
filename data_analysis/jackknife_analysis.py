import os
import sys
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, load_config, prompt_user_choice
from plot_utils import plot_jackknife_blocking_variance
from jackknife_utils import perform_jackknife_blocking
from interface_utils import navigate_directories

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
        output_dir = config['paths']['output_dir']
        input_paths = config['paths']['default_files']
        plot_dir = config['paths']['plot_dir']

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

            output_dir_input = input("Enter output data directory (default: {}): ".format(output_dir)).strip()
            output_dir = output_dir_input if output_dir_input else output_dir

            plot_dir_input = input("Enter output data directory (default: {}): ".format(plot_dir)).strip()
            plot_dir = plot_dir_input if plot_dir_input else plot_dir
            
            # Optionally select input paths from directories
            input_paths = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")

        
        # Perform analysis with the loaded settings
        if prompt_user_choice("Do you want to perform jackknife + blocking?"):
            perform_jackknife_blocking(input_paths, output_dir, first_index, num_cores, max_block_size)

        # Ask for the plots
        if prompt_user_choice("Do you want to plot?"):
            filepaths_to_plot = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")
            ensure_directory(plot_dir)
            for file in filepaths_to_plot:
                df = pd.read_csv(file)
                base_name = os.path.splitext(os.path.basename(file))[0]
                blocksizes = df["block_size"]
                var_U = df["var_U"] 
                save_name = f"{base_name}_var_U.png"
                save_path = os.path.join(plot_dir, save_name)
                plot_jackknife_blocking_variance(var_U, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance")
                var_chi_prime = df["var_chi_prime"]
                save_name = f"{base_name}_var_chi_prime.png"
                save_path = os.path.join(plot_dir, save_name)
                plot_jackknife_blocking_variance(var_chi_prime, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance")

    except Exception as main_e:
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)
