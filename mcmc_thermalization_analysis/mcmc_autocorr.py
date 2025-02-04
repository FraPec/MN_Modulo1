import os
import sys
import logging
import numpy as np

# Add the utils directory to the system path for importing utility modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))

# Import utility functions
from io_utils import (
    setup_logging, load_binary_file, save_autocorrelations_to_csv, ensure_directory,
    get_unique_filename, check_existing_autocorr_file, load_autocorr_from_csv, load_config, 
    get_user_choice_for_existing_file, extract_lattice_side, extract_beta
    )
    
from mcmc_utils import compute_autocorrelations
from plot_utils import plot_autocorrelations
from interface_utils import navigate_directories, get_user_inputs_for_mcmc_termalization_analysys


    
    

if __name__ == "__main__":
    """
    Main script for MCMC autocorrelation analysis.
    Handles autocorrelation calculations, file saving, and plot generation with robust file handling.
    """

    # Set up logging
    setup_logging(log_dir="../logs", log_file="mcmc_autocorr.log")
    logging.info("Starting MCMC Autocorrelation Analysis...")

    # Collect user inputs
    user_inputs = get_user_inputs_for_mcmc_termalization_analysys(config_path="../configs/mcmc_termalization_config.yaml")
    input_paths = user_inputs["input_paths"]
    max_lag = user_inputs["max_lag"]
    data_dir = user_inputs["data_dir"]
    plot_dir = user_inputs["plot_dir"]
    separate_plots = user_inputs["separate_plots"]
    x_scale = user_inputs["x_scale"]
    y_scale = user_inputs["y_scale"]

    ensure_directory(data_dir)
    ensure_directory(plot_dir)


    # Load configuration at the start of the script
    config = load_config(config_path="../configs/mcmc_termalization_config.yaml")
    logging.info("Configuration loaded successfully.")

    for file in input_paths:
        logging.info(f"Processing file: {file}")
        base_name = os.path.splitext(os.path.basename(file))[0]

        # Generate CSV file path with user input for conflicts
        csv_file = get_unique_filename(data_dir, f"{base_name}_autocorr", ".csv", max_lag=max_lag)
        if check_existing_autocorr_file(csv_file):
            action = get_user_choice_for_existing_file(csv_file)
            if action == "overwrite":
                logging.info("Overwriting existing autocorrelation file...")
                # Recalculate data
                data = load_binary_file(file, 3)
                m_x, m_y, epsilon = data[:, 0], data[:, 1], data[:, 2]
                module_m = np.sqrt(m_x**2 + m_y**2)
        
                autocorr_matrix = compute_autocorrelations(data[:, :2], max_lag)
                autocorr_m = [np.corrcoef(module_m[:-lag], module_m[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]
                autocorr_epsilon = [np.corrcoef(epsilon[:-lag], epsilon[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]
        
                autocorr_data = {
                    "mx-mx": autocorr_matrix[:, 0, 0],
                    "mx-my": autocorr_matrix[:, 0, 1],
                    "my-mx": autocorr_matrix[:, 1, 0],
                    "my-my": autocorr_matrix[:, 1, 1],
                    "module_m": autocorr_m,
                    "epsilon": autocorr_epsilon
                }
                save_autocorrelations_to_csv(csv_file, autocorr_data)
            elif action == "new_name":
                logging.info("Saving autocorrelation results with a new name...")
                csv_file = get_unique_filename(data_dir, f"{base_name}_autocorr", ".csv")
                data = load_binary_file(file, 3)
                m_x, m_y, epsilon = data[:, 0], data[:, 1], data[:, 2]
                module_m = np.sqrt(m_x**2 + m_y**2)
        
                autocorr_matrix = compute_autocorrelations(data[:, :2], max_lag)
                autocorr_m = [np.corrcoef(module_m[:-lag], module_m[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]
                autocorr_epsilon = [np.corrcoef(epsilon[:-lag], epsilon[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]
        
                autocorr_data = {
                    "mx-mx": autocorr_matrix[:, 0, 0],
                    "mx-my": autocorr_matrix[:, 0, 1],
                    "my-mx": autocorr_matrix[:, 1, 0],
                    "my-my": autocorr_matrix[:, 1, 1],
                    "module_m": autocorr_m,
                    "epsilon": autocorr_epsilon
                }
                save_autocorrelations_to_csv(csv_file, autocorr_data)
            elif action == "exit":
                logging.info("Exiting script as per user request.")
                sys.exit(0)
            elif action == "plot_only":
                logging.info(f"Proceeding to plot using existing file: {csv_file}")
                autocorr_data = load_autocorr_from_csv(csv_file)
        
        else:
            data = load_binary_file(file, 3)
            m_x, m_y, epsilon = data[:, 0], data[:, 1], data[:, 2]
            module_m = np.sqrt(m_x**2 + m_y**2)

            # Compute autocorrelations
            autocorr_matrix = compute_autocorrelations(data[:, :2], max_lag)
            autocorr_m = [np.corrcoef(module_m[:-lag], module_m[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]
            autocorr_epsilon = [np.corrcoef(epsilon[:-lag], epsilon[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]

            # Save results
            autocorr_data = {
                "mx-mx": autocorr_matrix[:, 0, 0],
                "mx-my": autocorr_matrix[:, 0, 1],
                "my-mx": autocorr_matrix[:, 1, 0],
                "my-my": autocorr_matrix[:, 1, 1],
                "module_m": autocorr_m,
                "epsilon": autocorr_epsilon
            }
            save_autocorrelations_to_csv(csv_file, autocorr_data)

        
        
        
        # Generate title for the plots
        lattice_side = extract_lattice_side(file)  
        beta = extract_beta(file)                  
        plot_title = config["settings"]["plot_title_format"].format(
            lattice_side=lattice_side, beta=beta
        )

        # Generate plots
        plot_file_matrix = get_unique_filename(plot_dir, f"{base_name}_autocorr_matrix", ".png", max_lag=max_lag)
        plot_autocorrelations(
            [autocorr_data["mx-mx"], autocorr_data["mx-my"],
             autocorr_data["my-mx"], autocorr_data["my-my"]],
            ["mx-mx", "mx-my", "my-mx", "my-my"], 
            max_lag, 
            plot_file_matrix, 
            x_scale=x_scale,
            y_scale=y_scale,
            title=plot_title
        )
        logging.info(f"Plot saved to: {plot_file_matrix}")

        if separate_plots:
            plot_file_m = get_unique_filename(plot_dir, f"{base_name}_autocorr_module_m", ".png", max_lag=max_lag)
            plot_autocorrelations([autocorr_data["module_m"]], ["module_m"], max_lag, plot_file_m, y_scale='log')

            plot_file_epsilon = get_unique_filename(plot_dir, f"{base_name}_autocorr_epsilon", ".png", max_lag=max_lag)
            plot_autocorrelations([autocorr_data["epsilon"]], ["epsilon"], max_lag, 
            plot_file_epsilon, 
            x_scale=x_scale,
            y_scale=y_scale,
            title=plot_title
        )
        else:
            combined_plot_file = get_unique_filename(plot_dir, f"{base_name}_autocorr_combined", ".png", max_lag=max_lag)
            plot_autocorrelations([autocorr_data["module_m"], autocorr_data["epsilon"]],
                                  ["module_m", "epsilon"], max_lag, combined_plot_file, 
                                  x_scale=x_scale,
                                  y_scale=y_scale,
                                  title=plot_title
                                  )
        logging.info(f"Autocorrelation results and plots saved in '{data_dir}' and '{plot_dir}' respectively.")

    logging.info("MCMC Autocorrelation Analysis Completed.")
