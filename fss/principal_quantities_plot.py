import sys
import os
import logging
import numpy as np
import pandas as pd

# Add the utils directory to the system path to import custom utility functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import setup_logging, load_config, ensure_directory, prompt_user_choice
from plot_utils import plot_finite_size_scaling
from fss_utils import prepare_dataset_fss_plot
from interface_utils import get_user_input_for_fss_plot

if __name__ == '__main__':
    """
    Main to perform plots of means of principal variables vs beta,
    """
    # Setup logging
    log_dir = "../logs/"
    log_file = "principal_quantities_plot.log"
    setup_logging(log_dir=log_dir, log_file=log_file)
    
    try:
        # Load and verify the configuration
        config_path = "../configs/principal_quantities_plot.yaml"
        config = load_config(config_path)
        print("Loaded configuration:")
        for key, value in config.items():
            print(f"{key}: {value}\n")
        
        plot_dir = config["paths"]["plot_dir"]
        ensure_directory(plot_dir)

        df_means = pd.read_csv(config["paths"]["file_name_means"])
        df_vars = pd.read_csv(config["paths"]["file_name_vars"])
        
        # Remove duplicate rows
        df_means = df_means.drop_duplicates(subset=['L', 'beta'])
        df_vars = df_vars.drop_duplicates(subset=['L', 'beta']) 
        
        variables_to_plot = config["settings"]["variables_to_plot"]
        variables_names_latex = config["settings"]["variables_names_latex"]

        # Define limited L values for mx_mean and my_mean
        limited_L_values = [18, 24, 30]  # Specify the L values you want to keep
        dim = 3
        df_means["chi_mean"] = df_means["m2_mean"].values * df_means["beta"].values * df_means["L"].values**dim
        df_vars["var_chi"] = df_vars["var_m2"].values * df_vars["beta"].values * df_vars["L"].values**dim 
        df_means["mx_mean"] = df_means["mx_mean"] * 1e3
        df_means["my_mean"] = df_means["my_mean"] * 1e3
        df_vars["var_mx"] = df_vars["var_mx"] * 1e6
        df_vars["var_my"] = df_vars["var_my"] * 1e6

        for variable, variable_latex in zip(variables_to_plot, variables_names_latex):
            # Filter df_means and df_vars for limited L values if the variable is mx_mean or my_mean
            if variable in ["mx_mean", "my_mean"]:
                df_means_filtered = df_means[df_means["L"].isin(limited_L_values)]
                df_vars_filtered = df_vars[df_vars["L"].isin(limited_L_values)]
            else:
                df_means_filtered = df_means
                df_vars_filtered = df_vars
            
            save_path = os.path.join(plot_dir, f"{variable}_vs_beta_different_L.png")
            
            # Prepare the dataset for plotting
            beta_list, means_data_set_list, std_devs_data_set_list, L_list = prepare_dataset_fss_plot(
                df_means_filtered, variable, df_vars=df_vars_filtered
            )
            
            # Plot with errors
            if variable in ["mx_mean", "my_mean"]:
                plot_finite_size_scaling(
                    beta_list, means_data_set_list, errors=std_devs_data_set_list, lattice_side_list=L_list, 
                    marker='.', linestyle='', cmap='tab10', xlabel=r"$\beta$", ylabel=variable_latex, save_path=save_path,
                    x_interval=[0.451, 0.454]
                )
            else:
                plot_finite_size_scaling(
                    beta_list, means_data_set_list, errors=std_devs_data_set_list, lattice_side_list=L_list, 
                    marker='.', linestyle='--', cmap='tab10', xlabel=r"$\beta$", ylabel=variable_latex, save_path=save_path
                )
    except Exception as main_e:
        # Log any unexpected errors
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)

