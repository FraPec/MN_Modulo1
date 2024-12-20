import os
import yaml
import logging
import csv
import numpy as np


def setup_logging(log_dir="logs", log_file="mcmc_autocorr.log"):
    """
    Sets up the logging system to log messages to a file and the console.

    Parameters:
        log_dir (str): Directory where the log file will be saved.
        log_file (str): Name of the log file.

    Returns:
        None
    """
    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[INFO] Created log directory: {log_dir}")

    # Full path to the log file
    log_path = os.path.join(log_dir, log_file)

    # Configure the logging system
    logging.basicConfig(
        level=logging.INFO,  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),  # Save logs to a file
            logging.StreamHandler()         # Print logs to the console
        ]
    )

    logging.info("Logging system initialized.")  # Example log entry

def ensure_directory(directory):
    """
    Ensures that a directory exists. If not, it is created.

    Parameters:
        directory (str): Path to the directory.

    Returns:
        None
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.info(f"Directory already exists: {directory}")

def load_config(config_path="config.yaml"):
    """
    Loads a YAML configuration file.

    Parameters:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Parsed configuration data.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    logging.info("Configuration loaded successfully.")
    return config

def load_binary_file(filepath, n_cols):
    """
    Loads binary files and reshapes them into a NumPy array.

    Parameters:
        filepath (str): Path to the binary file.
        n_cols (int): Number of columns the data should have.

    Returns:
        np.ndarray: Reshaped binary data.
    """
    data = np.fromfile(filepath, dtype=np.float64)
    if data.size % n_cols != 0:
        raise ValueError("The binary file cannot be reshaped into the specified columns.")
    return data.reshape(-1, n_cols)



def save_autocorr_to_csv(filepath, data, headers):
    """
    Saves autocorrelation data to a CSV file.

    Parameters:
        filepath (str): Path to save the CSV file.
        data (np.ndarray): Array of autocorrelation data.
        headers (list): List of column headers for the CSV.

    Returns:
        None
    """
    logging.info(f"Saving autocorrelation data to: {filepath}")
    with open(filepath, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write headers
        writer.writerows(data)  # Write data rows
    logging.info("Autocorrelation data successfully saved.")




def get_unique_filename(directory, base_name, extension):
    """
    Ensures unique filenames to prevent overwriting.

    Parameters:
        directory (str): Directory where the file will be saved.
        base_name (str): Base name for the file.
        extension (str): File extension.

    Returns:
        str: Unique file path.
    """
    file_path = os.path.join(directory, f"{base_name}{extension}")
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(directory, f"{base_name}_v{counter}{extension}")
        counter += 1
    return file_path
    
    
    
def prompt_user_choice(message):
    """
    Prompts the user for a yes/no choice.

    Parameters:
        message (str): The prompt message.

    Returns:
        bool: True if the user selects 'y', False otherwise.
    """
    while True:
        choice = input(f"{message} (y/n): ").strip().lower()
        if choice in ["y", "n"]:
            return choice == "y"
        print("Invalid input. Please enter 'y' or 'n'.")    
    
    