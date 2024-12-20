import os
import sys
import logging
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import (
    setup_logging, load_binary_file, save_autocorr_to_csv, ensure_directory,
    get_unique_filename, prompt_user_choice
)
from mcmc_utils import compute_autocorrelations
from plot_utils import plot_autocorrelations
from interface_utils import get_user_inputs




if __name__ == "__main__":
	
    """
    Main function for MCMC autocorrelation analysis.
    """
    # Setup logging
    setup_logging()
    logging.info("Starting MCMC Autocorrelation Analysis...")

    # Collect user inputs
    user_inputs = get_user_inputs()
    input_path = user_inputs["input_path"]
    max_lag = user_inputs["max_lag"]
    data_dir = user_inputs["data_dir"]
    plot_dir = user_inputs["plot_dir"]
    separate_plots = user_inputs["separate_plots"]

    # Ensure directories exist
    ensure_directory(data_dir)
    ensure_directory(plot_dir)

    # Process input file(s)
    files = [input_path] if os.path.isfile(input_path) else [
        os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(('.bin', '.dat'))
    ]

    for file in files:
        logging.info(f"Processing file: {file}")
        data = load_binary_file(file, 3)
        m_x, m_y, epsilon = data[:, 0], data[:, 1], data[:, 2]
        m = np.sqrt(m_x**2 + m_y**2)

        # Compute autocorrelations
        autocorr_matrix = compute_autocorrelations(data[:, :2], max_lag)
        autocorr_m = [np.corrcoef(m[:-lag], m[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]
        autocorr_epsilon = [np.corrcoef(epsilon[:-lag], epsilon[lag:])[0, 1] if lag > 0 else 1 for lag in range(max_lag + 1)]

        # Save autocorrelation data to CSV
        base_name = os.path.splitext(os.path.basename(file))[0]
        csv_file = get_unique_filename(data_dir, f"{base_name}_autocorr", ".csv")
        save_autocorr_to_csv(csv_file, np.column_stack((
            autocorr_matrix[:, 0, 0], autocorr_matrix[:, 0, 1],
            autocorr_matrix[:, 1, 0], autocorr_matrix[:, 1, 1],
            autocorr_m, autocorr_epsilon
        )), headers=["mx-mx", "mx-my", "my-mx", "my-my", "module_m", "epsilon"])

        # Plot autocorrelations
        plot_file_matrix = get_unique_filename(plot_dir, f"{base_name}_autocorr_matrix", ".png")
        plot_autocorrelations(
            [autocorr_matrix[:, 0, 0], autocorr_matrix[:, 0, 1],
             autocorr_matrix[:, 1, 0], autocorr_matrix[:, 1, 1]],
            ["mx-mx", "mx-my", "my-mx", "my-my"], max_lag, plot_file_matrix, y_scale='log'
        )

        if separate_plots:
            plot_file_m = get_unique_filename(plot_dir, f"{base_name}_autocorr_module_m", ".png")
            plot_autocorrelations([autocorr_m], ["module_m"], max_lag, plot_file_m, y_scale='log')

            plot_file_epsilon = get_unique_filename(plot_dir, f"{base_name}_autocorr_epsilon", ".png")
            plot_autocorrelations([autocorr_epsilon], ["epsilon"], max_lag, plot_file_epsilon, y_scale='log')
        else:
            combined_plot_file = get_unique_filename(plot_dir, f"{base_name}_autocorr_combined", ".png")
            plot_autocorrelations([autocorr_m, autocorr_epsilon], ["module_m", "epsilon"], max_lag, combined_plot_file, y_scale='log')

    logging.info("MCMC Autocorrelation Analysis Completed.")
