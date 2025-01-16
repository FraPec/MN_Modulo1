import sys
import os
import logging
import numpy as np
import pandas as pd

# Add the utils directory to the system path to import custom utility functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import setup_logging, load_config, ensure_directory, prompt_user_choice
from plot_utils import plot_fss_with_errors
from fss_utils import prepare_dataset_fss_plot
from interface_utils import get_user_input_for_fss_plot

if __name__=='__main__':
    """
    Main to perform plots of means of secondary variables vs beta, 
    with relative standard deviations as errors on y axis
    """
    # Setup logging
    log_dir = "../logs/"
    log_file = "fss_plot.log"
    setup_logging(log_dir=log_dir, log_file=log_file)
    
    try:
        # Load and verify the configuration
        config_path = "../configs/fss.yaml"
        config = load_config(config_path)
        print("Loaded configuration:")
        for key, value in config.items():
            print(f"{key}: {value}\n")
        
        # Ask the user if they want to adjust the configuration
        if not prompt_user_choice("Is this configuration correct?"):
            config = get_user_input_for_fss_plot(config)
        
        plot_dir = config["paths"]["plot_dir"]
        ensure_directory(plot_dir)

        df_means = pd.read_csv(config["paths"]["file_name_means"])
        df_vars = pd.read_csv(config["paths"]["file_name_vars"])
        
        variables_to_plot = config["settings"]["variables_to_plot"]
        variables_names_latex = config["settings"]["variables_names_latex"]
        
        for variable, variable_latex in zip(variables_to_plot, variables_names_latex):
            save_path = os.path.join(plot_dir, f"{variable}_vs_beta_different_L.png")
            beta_list, means_data_set_list, std_devs_data_set_list, L_list = prepare_dataset_fss_plot(df_means, df_vars, variable)
            plot_fss_with_errors(beta_list, means_data_set_list, std_devs_data_set_list, lattice_side_list=L_list, marker='o', cmap='tab10', xlabel="beta", ylabel=variable_latex, save_path=save_path)
        
    except Exception as main_e:
        # Log any unexpected errors
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)

