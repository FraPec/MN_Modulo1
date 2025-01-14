import os
import sys
import logging
import pandas as pd
import numpy as np

# Add the utils directory to the system path to import custom utility functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, load_config, prompt_user_choice
from plot_utils import plot_jackknife_blocking_variance
from jackknife_utils import perform_jackknife_blocking
from interface_utils import navigate_directories

if __name__ == "__main__":
    """
    Main script for performing Jackknife analysis on lattice metrics.
    The script reads configuration, processes data, and optionally generates plots.
    """
    # Setup logging to capture important events and errors
    log_dir = "../logs"  # Default log directory
    log_file = "jackknife_analysis.log"  # Default log file name
    setup_logging(log_dir=log_dir, log_file=log_file)
    
    try:
        # Load configuration from the specified YAML file
        config_path = "../configs/jackknife_config.yaml"
        config = load_config(config_path)

        # Extract relevant settings from the loaded configuration
        first_index = config['settings']['first_index']
        max_block_size = config['settings']['max_block_size_default']
        num_cores = config['settings']['num_cores_default']
        data_columns = config['settings']['data_columns']
        log_dir = config['paths']['log_dir']
        output_dir = config['paths']['output_dir']
        input_paths = config['paths']['default_files']
        plot_dir = config['paths']['plot_dir']

        # Print the loaded configuration for user verification
        print("Loaded configuration:")
        for key, value in config.items():
            print(f"{key}: {value}\n")

        # Ask the user to confirm the loaded configuration
        if not prompt_user_choice("Is this configuration correct?"):
            # If the configuration is incorrect, prompt for each parameter individually
            first_index_input = input(f"Enter first index (default: {first_index}): ").strip()
            first_index = int(first_index_input) if first_index_input else first_index

            max_block_size_input = input(f"Enter max block size (default: {max_block_size}): ").strip()
            max_block_size = int(max_block_size_input) if max_block_size_input else max_block_size

            num_cores_input = input(f"Enter number of cores (default: {num_cores}): ").strip()
            num_cores = int(num_cores_input) if num_cores_input else num_cores

            # Prompt for data columns as a comma-separated string
            data_columns_input = input(f"Enter data columns as comma-separated values (default: {','.join(data_columns)}): ").strip()
            data_columns = data_columns_input.split(',') if data_columns_input else data_columns

            # Prompt for directory paths
            log_dir_input = input(f"Enter log directory (default: {log_dir}): ").strip()
            log_dir = log_dir_input if log_dir_input else log_dir

            output_dir_input = input(f"Enter output data directory (default: {output_dir}): ").strip()
            output_dir = output_dir_input if output_dir_input else output_dir

            plot_dir_input = input(f"Enter plot directory (default: {plot_dir}): ").strip()
            plot_dir = plot_dir_input if plot_dir_input else plot_dir
            
            # Optionally select input paths from directories using a file picker
            input_paths = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")

        # Ask the user if they want to perform jackknife + blocking analysis
        if prompt_user_choice("Do you want to perform jackknife + blocking?"):
            # Perform the Jackknife blocking analysis on the selected input files
            perform_jackknife_blocking(input_paths, output_dir, first_index, num_cores, max_block_size)

        # Ask the user if they want to generate plots from the analysis
        if prompt_user_choice("Do you want to plot?"):
            # Let the user select which files to plot
            filepaths_to_plot = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")
            
            # Ensure the plot directory exists
            ensure_directory(plot_dir)

            # Iterate over each file selected for plotting
            for file in filepaths_to_plot:
                # Read the data from the selected CSV file
                df = pd.read_csv(file)
                base_name = os.path.splitext(os.path.basename(file))[0]

                # Extract the necessary columns for plotting
                blocksizes = df["block_size"]
                var_U = df["var_U"]
                
                # Generate a plot for the variance of U and save it
                save_name = f"{base_name}_var_U.png"
                save_path = os.path.join(plot_dir, save_name)
                plot_jackknife_blocking_variance(var_U, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance")
                
                # Extract the necessary column for chi prime and generate a plot
                var_chi_prime = df["var_chi_prime"]
                save_name = f"{base_name}_var_chi_prime.png"
                save_path = os.path.join(plot_dir, save_name)
                plot_jackknife_blocking_variance(var_chi_prime, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance")

    except Exception as main_e:
        # Log any unexpected errors during script execution
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)

