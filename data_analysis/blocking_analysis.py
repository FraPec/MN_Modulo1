import os
import sys
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging
from blocking_utils import calculate_blocking_variances
from plot_utils import plot_blocking_variance
from interface_utils import get_user_inputs_for_blocking_analysis


def check_existing_files(blocking_csv, plot_files):
    """
    Check for existing blocking CSV and plot files, and prompt user for action.

    Parameters:
        blocking_csv (str): Path to the blocking CSV file.
        plot_files (list): List of paths to plot files.

    Returns:
        dict: User's choices for processing and plotting.
    """
    user_choices = {"recompute_blocking": True, "replot": True}  # Default to recompute and replot if files don't exist

    # Check for existing blocking CSV
    if os.path.exists(blocking_csv):
        logging.warning(f"Blocking CSV file already exists: {blocking_csv}")
        choice = input(f"Blocking file exists. Overwrite (o), use for plots only (p), or skip (s)? ").strip().lower()
        if choice == "o":
            user_choices["recompute_blocking"] = True
        elif choice == "p":
            user_choices["recompute_blocking"] = False
        elif choice == "s":
            user_choices["recompute_blocking"] = None

    # Check for existing plot files
    existing_plots = [p for p in plot_files if os.path.exists(p)]
    if existing_plots:
        logging.warning(f"Plot files already exist: {existing_plots}")
        choice = input(f"Plots exist. Overwrite (o) or skip (s)? ").strip().lower()
        if choice == "o":
            user_choices["replot"] = True
        elif choice == "s":
            user_choices["replot"] = False

    return user_choices


def process_csv_for_blocking(input_file, output_dir, plot_dir, max_block_size, num_cores):
    """
    Process a single CSV file to apply blocking analysis and save results.

    Parameters:
        input_file (str): Path to the input CSV file.
        output_dir (str): Directory to save blocking results.
        plot_dir (str): Directory to save blocking plots.
        max_block_size (int): Maximum block size for the analysis.
        num_cores (int): Number of CPU cores to use for parallel processing.

    Returns:
        None
    """
    logging.info(f"Processing CSV file: {input_file}")
    
    # Read the input file
    try:
        data = pd.read_csv(input_file)
    except Exception as e:
        logging.error(f"Failed to read CSV file {input_file}: {e}")
        return

    # Extract lattice and beta from the file name
    lattice_side = data["L"].iloc[0]
    beta = data["beta"].iloc[0]

    # Prepare output directories
    lattice_csv_dir = os.path.join(output_dir, f"L{lattice_side}")
    ensure_directory(lattice_csv_dir)

    lattice_plot_dir = os.path.join(plot_dir, f"L{lattice_side}")
    ensure_directory(lattice_plot_dir)

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    file_plot_dir = os.path.join(lattice_plot_dir, base_name)
    ensure_directory(file_plot_dir)

    # Paths for blocking CSV and plot files
    blocking_csv = os.path.join(lattice_csv_dir, f"{base_name}_blocking_{max_block_size}.csv")
    plot_files = [os.path.join(file_plot_dir, f"L{lattice_side}_beta{beta}_{column}_blocking_{max_block_size}.png") for column in ["mx", "my", "epsilon", "absm", "m2", "m4"]]

    # Check existing files and prompt for actions
    user_choices = check_existing_files(blocking_csv, plot_files)
    if user_choices["recompute_blocking"] is None:
        logging.info("Skipping processing for this file.")
        return

    # Prepare results storage
    results = {"block_size": range(1, max_block_size + 1)}

    # Process each column for blocking analysis
    columns_to_process = ["mx", "my", "epsilon", "absm", "m2", "m4"]
    for column in columns_to_process:
        if column not in data.columns:
            logging.warning(f"Column '{column}' not found in {input_file}. Skipping...")
            continue
        
        if user_choices["recompute_blocking"]:
            # Calculate variances if required
            column_data = data[column].to_numpy()
            logging.info(f"Performing blocking analysis for column: {column}")
            try:
                variances = calculate_blocking_variances(column_data, max_block_size, num_cores)
                results[f"var_{column}"] = list(variances.values())
            except Exception as e:
                logging.error(f"Error during blocking analysis for {column}: {e}")
                continue
        else:
            # Load existing variances from CSV
            try:
                logging.info(f"Loading blocking data for column: {column} from {blocking_csv}")
                csv_data = pd.read_csv(blocking_csv)
                variances = dict(zip(csv_data["block_size"], csv_data[f"var_{column}"]))
            except Exception as e:
                logging.error(f"Failed to load blocking data for column {column} from {blocking_csv}: {e}")
                continue

        # Generate plot if required
        if user_choices["replot"]:
            try:
                plot_file = os.path.join(file_plot_dir, f"L{lattice_side}_beta{beta}_{column}_blocking_{max_block_size}.png")
                plot_blocking_variance(
                    variances=variances,
                    save_path=plot_file,
                    title=f"Blocking Analysis for {column} (L={lattice_side}, β={beta}, max_block_size={max_block_size})"
                )
                logging.info(f"Plot saved: {plot_file}")
            except Exception as e:
                logging.error(f"Error generating plot for {column}: {e}")

    # Save results to CSV if recomputing blocking
    if user_choices["recompute_blocking"]:
        results_df = pd.DataFrame(results)
        results_df.to_csv(blocking_csv, index=False)
        logging.info(f"Blocking results saved to: {blocking_csv}")


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
        num_cores = user_inputs["num_cores"]

        # Ensure output directories exist
        ensure_directory(output_dir)
        ensure_directory(plot_dir)

        # Process each selected path
        for input_path in input_paths:
            if os.path.isdir(input_path):
                # If it's a directory, process all valid files inside
                for csv_file in sorted(os.listdir(input_path)):
                    if csv_file.endswith("_summary.csv"):
                        input_file = os.path.join(input_path, csv_file)
                        process_csv_for_blocking(input_file, output_dir, plot_dir, max_block_size, num_cores)
            elif os.path.isfile(input_path):
                # If it's a single file, process it directly
                process_csv_for_blocking(input_path, output_dir, plot_dir, max_block_size, num_cores)

    except Exception as main_e:
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)