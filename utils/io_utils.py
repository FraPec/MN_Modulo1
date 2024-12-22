import os
import sys
import yaml
import logging
import csv
import numpy as np
import pandas as pd
import re



def setup_logging(log_dir="../logs", log_file="log_file.log"):
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




prompt_cache = {}  # Cache for user's decisions

def get_user_choice_for_existing_file(file_path):
    """
    Prompt the user to decide what to do when a file already exists.

    Parameters:
        file_path (str): Path to the existing file.

    Returns:
        str: Action chosen by the user ('overwrite', 'new_name', 'exit', 'plot_only').
    """
    # Check if the user has already decided for this file type
    if file_path in prompt_cache:
        return prompt_cache[file_path]

    while True:
        print(f"\n[WARNING] File '{file_path}' already exists.")
        print("Options:")
        print("  1. Overwrite the file")
        print("  2. Save with a new name")
        print("  3. Exit script")
        print("  4. Proceed directly to plotting using this file")
        choice = input("Enter your choice (1/2/3/4): ").strip()
        if choice == "1":
            prompt_cache[file_path] = "overwrite"
            return "overwrite"
        elif choice == "2":
            prompt_cache[file_path] = "new_name"
            return "new_name"
        elif choice == "3":
            prompt_cache[file_path] = "exit"
            return "exit"
        elif choice == "4":
            prompt_cache[file_path] = "plot_only"
            return "plot_only"
        else:
            print("[ERROR] Invalid input. Please enter 1, 2, 3, or 4.")

def get_unique_filename(directory, base_name, extension, max_lag=None):
    """
    Ensures unique filenames to prevent overwriting. Provides options to overwrite or rename.

    Parameters:
        directory (str): Directory where the file will be saved.
        base_name (str): Base name for the file.
        extension (str): File extension.
        max_lag (int, optional): Maximum lag value to include in the filename.

    Returns:
        str: Final file path chosen by the user.
    """
    # Include max_lag in the base name if provided
    if max_lag is not None:
        base_name = f"{base_name}_lag{max_lag}"

    file_path = os.path.join(directory, f"{base_name}{extension}")
    if os.path.exists(file_path):
        action = get_user_choice_for_existing_file(file_path)
        if action == "overwrite":
            return file_path
        elif action == "new_name":
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(directory, f"{base_name}_v{counter}{extension}")
                counter += 1
            print(f"[INFO] New file name: {file_path}")
        elif action == "exit":
            print("[INFO] Exiting script as per user request.")
            sys.exit(0)
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
        
        
        
        
        

def load_autocorr_from_csv(csv_path):
    """
    Load autocorrelations from an existing CSV file.

    Parameters:
        csv_path (str): Path to the CSV file.

    Returns:
        dict: Dictionary containing loaded autocorrelations.
    """
    df = pd.read_csv(csv_path)
    return {
        "mx-mx": df["mx-mx"].to_numpy(),
        "mx-my": df["mx-my"].to_numpy(),
        "my-mx": df["my-mx"].to_numpy(),
        "my-my": df["my-my"].to_numpy(),
        "module_m": df["module_m"].to_numpy(),
        "epsilon": df["epsilon"].to_numpy()
    }


def save_autocorrelations_to_csv(file_path, autocorr_dict):
    """
    Save autocorrelation results to a CSV file.

    Parameters:
        file_path (str): Path to save the CSV file.
        autocorr_dict (dict): Dictionary of autocorrelation arrays.

    Returns:
        None
    """
    # Convert dictionary to a DataFrame
    df = pd.DataFrame({
        "mx-mx": autocorr_dict["mx-mx"],
        "mx-my": autocorr_dict["mx-my"],
        "my-mx": autocorr_dict["my-mx"],
        "my-my": autocorr_dict["my-my"],
        "module_m": autocorr_dict["module_m"],
        "epsilon": autocorr_dict["epsilon"]
    })
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    print(f"[INFO] Autocorrelation results saved to: {file_path}")
    
    


def check_existing_autocorr_file(file_path):
    """
    Check if an autocorrelation file already exists.

    Parameters:
        file_path (str): Path to the autocorrelation file.

    Returns:
        bool: True if file exists, False otherwise.
    """
    return os.path.isfile(file_path)
    
    
    


def extract_lattice_side(file_path):
    """
    Extract the lattice side from the file name based on a naming convention.
    Example: "data_b0.456_a1.0_L15.bin" -> lattice_side = 15

    Parameters:
        file_path (str): Path to the file.

    Returns:
        int: Lattice side extracted from the file name, or None if not found.
    """
    # Regex pattern to match '_L<number>'
    match = re.search(r"_L(\d+)", file_path)
    if match:
        return int(match.group(1))
    else:
        logging.warning(f"Lattice side not found in file name: {file_path}")
        return None


def extract_beta(file_path):
    """
    Extract the beta value from the file name based on a naming convention.
    Example: "data_b0.456_a1.0_L15.bin" -> beta = 0.456

    Parameters:
        file_path (str): Path to the file.

    Returns:
        float: Beta value extracted from the file name, or None if not found.
    """
    # Regex pattern to match 'b<number>'
    match = re.search(r"_b([\d\.]+)", file_path)
    if match:
        return float(match.group(1))
    else:
        logging.warning(f"Beta value not found in file name: {file_path}")
        return None
        
        
        
def save_blocking_results(output_path, variances, headers=None):
    """
    Save blocking results to a CSV file.
    """
    ensure_directory(os.path.dirname(output_path))
    with open(output_path, "w") as file:
        if headers:
            file.write(",".join(headers) + "\n")
        for block_size, variance in variances.items():
            file.write(f"{block_size},{variance}\n")
            
            
 
            
            
            
def save_lattice_metrics_to_csv(output_dir, lattice_side, beta, metrics):
    """
    Save the metrics to a CSV file with one row per data point.

    Parameters:
        output_dir (str): Path to the output directory.
        lattice_side (int): Lattice side extracted from the filename.
        beta (float): Beta value extracted from the filename.
        metrics (dict): Metrics calculated for the input data.
    """
    # Ensure lattice-specific subdirectory exists
    lattice_dir = os.path.join(output_dir, f"L{lattice_side}")
    ensure_directory(lattice_dir)

    # Construct output file name
    output_file = os.path.join(lattice_dir, f"data_L{lattice_side}_b{beta:.3f}_summary.csv")

    # Add L and beta to each row
    num_rows = len(metrics["mx"])  # Assumes all metrics have the same length
    data = {
        "L": [lattice_side] * num_rows,
        "beta": [beta] * num_rows,
        **metrics  # Expand metrics dictionary into columns
    }
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"[INFO] Saved CSV file: {output_file}")
    