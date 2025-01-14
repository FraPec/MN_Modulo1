import os
import sys
import logging
import pandas as pd
import numpy as np

# Add the utils directory to the system path to import custom utility functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, load_config, prompt_user_choice
from jackknife_utils import plot_jackknife_variances, perform_jackknife_blocking_analysis
from interface_utils import navigate_directories, get_user_inputs_for_jackknife


if __name__ == "__main__":
    """
    Main script for performing Jackknife analysis on lattice metrics.
    The script reads configuration, processes data, and optionally generates plots.
    """
    # Setup logging
    log_dir = "../logs"
    log_file = "jackknife_analysis.log"
    setup_logging(log_dir=log_dir, log_file=log_file)

    try:
        # Load and verify the configuration
        config_path = "../configs/jackknife_config.yaml"
        config = load_config(config_path)
        print("Loaded configuration:")
        for key, value in config.items():
            print(f"{key}: {value}\n")

        # Ask the user if they want to adjust the configuration
        if not prompt_user_choice("Is this configuration correct?"):
            config = get_user_inputs_for_jackknife(config)

        # Perform the Jackknife blocking analysis if confirmed by the user
        if prompt_user_choice(f"Do you want to perform jackknife + blocking for all blocksizes less than {config['settings']['max_block_size_default']}?"):
            perform_jackknife_blocking_analysis(config['paths']['default_files'], config['paths']['output_dir'], 
                                       config['settings']['first_index'], config['settings']['num_cores_default'], 
                                       config['settings']['max_block_size_default'])

        # Generate plots if requested
        if prompt_user_choice("Do you want to plot?"):
            filepaths_to_plot = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")
            ensure_directory(config['paths']['plot_dir'])

            # Iterate over selected files and plot variances
            for file in filepaths_to_plot:
                df = pd.read_csv(file)
                base_name = os.path.splitext(os.path.basename(file))[0]
                plot_jackknife_variances(df, config['paths']['plot_dir'], base_name)

    except Exception as main_e:
        # Log any unexpected errors
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)


