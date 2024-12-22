import os
import sys
import pandas as pd
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, extract_lattice_side, extract_beta, load_config
from interface_utils import get_user_inputs_for_principal_quantities_means



def process_blocking_files(input_dir, output_dir, output_file, block_size_threshold, csv_output_header):
    """
    Process blocking data files to extract variances at a given block size threshold.

    Parameters:
        input_dir (str): Directory containing blocking data files.
        output_dir (str): Directory to save the summary CSV.
        output_file (str): Name of the output summary file.
        block_size_threshold (int): The block size for which to extract variances.
        csv_output_header (list): The output CSV header.
    """
    logging.info(f"Processing blocking data in directory: {input_dir}")
    ensure_directory(output_dir)

    summary_data = []

    for subdir in sorted(os.listdir(input_dir)):
        subdir_path = os.path.join(input_dir, subdir)
        if os.path.isdir(subdir_path):
            logging.info(f"Processing subdirectory: {subdir_path}")
            for file in sorted(os.listdir(subdir_path)):
                if file.endswith(".csv"):
                    file_path = os.path.join(subdir_path, file)
                    logging.info(f"Processing file: {file_path}")
                    try:
                        df = pd.read_csv(file_path)

                        # Extract L and beta using utility functions
                        L = extract_lattice_side(file_path)
                        beta = extract_beta(file_path)
                        if L is None or beta is None:
                            continue

                        # Select the row corresponding to the block size threshold
                        row = df[df["block_size"] == block_size_threshold]
                        if row.empty:
                            logging.warning(f"No data found for block_size = {block_size_threshold} in {file_path}")
                            continue

                        # Extract variances
                        summary_data.append({
                            "L": L,
                            "beta": beta,
                            "var_mx": row["var_mx"].iloc[0],
                            "var_my": row["var_my"].iloc[0],
                            "var_epsilon": row["var_epsilon"].iloc[0],
                            "var_absm": row["var_absm"].iloc[0],
                            "var_m2": row["var_m2"].iloc[0],
                            "var_m4": row["var_m4"].iloc[0]
                        })
                    except Exception as e:
                        logging.error(f"Failed to process file {file_path}: {e}")

    # Save summary data to CSV
    output_path = os.path.join(output_dir, output_file)
    summary_df = pd.DataFrame(summary_data, columns=csv_output_header)
    summary_df.to_csv(output_path, index=False)
    logging.info(f"Summary saved to {output_path}")

if __name__ == "__main__":
    """
    Main script for extracting blocking variances and saving them to a summary CSV.
    """
    setup_logging(log_dir="../logs", log_file="blocking_variances_to_csv.log")

    # Load configuration
    config_path = "../configs/blocking_variances_to_csv_config.yaml"
    config = load_config(config_path)

    # Extract settings and paths from the configuration
    settings = config["settings"]
    paths = config["paths"]

    block_size_threshold_default = settings["block_size_threshold_default"]
    csv_output_header = settings["csv_output_header"]

    # Get user inputs
    user_inputs = get_user_inputs_for_principal_quantities_means(config_path)
    input_dir = user_inputs["input_dir"]
    output_dir = user_inputs["output_dir"]
    output_file = user_inputs["output_file"]

    # Prompt user for block size threshold
    block_size_threshold = input(
        f"Enter block size threshold (Default: {block_size_threshold_default}): "
    ).strip()
    if not block_size_threshold:
        block_size_threshold = block_size_threshold_default
    else:
        try:
            block_size_threshold = int(block_size_threshold)
        except ValueError:
            logging.error("Invalid block size threshold entered. Using default.")
            block_size_threshold = block_size_threshold_default

    process_blocking_files(
        input_dir=input_dir,
        output_dir=output_dir,
        output_file=output_file,
        block_size_threshold=block_size_threshold,
        csv_output_header=csv_output_header
    )