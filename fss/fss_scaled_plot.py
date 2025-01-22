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
    Main to perform plots of means of secondary variables vs beta,
    without using errors (variance-related data).
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

        variables_to_plot = config["settings"]["scaled_variables_to_plot"]
        variables_names_latex = config["settings"]["scaled_variables_names_latex"]
        
        gamma, nu, beta_c = config["critical_values"]["gamma"], config["critical_values"]["nu"], config["critical_values"]["beta_c"]
        dim = 3
        alpha = 2 - nu * dim

        df_means["chi_prime_mean"] = df_means["chi_prime_mean"].values / (df_means["L"].values)**(gamma/nu)
        df_means["C_mean"] = df_means["C_mean"].values / (df_means["L"].values)**(alpha/nu)
        df_means["beta"] = (df_means["beta"].values - beta_c) * (df_means["L"].values)**(1/nu)    
        
        for variable, variable_latex in zip(variables_to_plot, variables_names_latex):
            save_path = os.path.join(plot_dir, f"{variable}_vs_beta_different_L_scaled.png")
            # Prepare the dataset for plotting, without using variance data
            beta_list, means_data_set_list, L_list = prepare_dataset_fss_plot(df_means, variable)
            
            # Plot without errors (no variance data)
            plot_finite_size_scaling(beta_list, means_data_set_list, errors=None, lattice_side_list=L_list, 
                                     marker='.', cmap='tab10', xlabel=r"$(\beta - \beta_c) L^{1/\nu}$", ylabel=variable_latex, save_path=save_path)
        
        beta_exponent = (nu * dim - gamma) / 2
        df_means = pd.read_csv(config["paths"]["absm"])
        df_means["beta"] = (df_means["beta"].values - beta_c) * (df_means["L"].values)**(1/nu)
        df_means["absm_mean"] = df_means["absm_mean"].values * (df_means["L"].values)**(beta_exponent/nu)
        
        save_path = os.path.join(plot_dir, f"absm_vs_beta_different_L_scaled.png")
        beta_list, means_data_set_list, L_list = prepare_dataset_fss_plot(df_means, "absm")
        
        # Plot without errors (no variance data)
        plot_finite_size_scaling(beta_list, means_data_set_list, errors=None, lattice_side_list=L_list, 
                                 marker='.', cmap='tab10', xlabel=r"$(\beta - \beta_c) L^{1/\nu}$", ylabel=r"$<|\mathbf{m}|> L^{\beta / \nu}$", save_path=save_path)

    except Exception as main_e:
        # Log any unexpected errors
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)

