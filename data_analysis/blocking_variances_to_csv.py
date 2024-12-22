import os
import sys
import pandas as pd
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import ensure_directory, setup_logging, extract_lattice_side, extract_beta, load_config
from interface_utils import get_user_inputs_for_principal_quantities_means
from blocking_utils import process_blocking_files



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