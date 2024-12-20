import os
import logging

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import load_config, ensure_directory



def get_user_inputs(config_path="config.yaml"):
    """
    Interactive interface to ask the user for inputs and preferences.

    Parameters:
        config_path (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing all user inputs and preferences.
    """
    # Load default values from config
    config = load_config(config_path)
    defaults = config["settings"]
    paths = config["paths"]

    print("\n===== MCMC Autocorrelation Analysis =====\n")

    # Ask for the input file or folder
    while True:
        input_path = input(
            "Enter the path to the input file or folder: "
        ).strip()
        if os.path.exists(input_path):
            break
        print("[ERROR] Path does not exist. Please try again.")

    # Ask for max_lag
    max_lag_default = defaults["max_lag_default"]
    while True:
        max_lag_input = input(
            f"Enter the maximum lag for autocorrelations (Default: {max_lag_default}): "
        ).strip()
        if not max_lag_input:
            max_lag = max_lag_default  # Use default if input is empty
            break
        try:
            max_lag = int(max_lag_input)
            break
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")

    # Ask for output preferences
    print("\nOutput Directories:")
    print(f"  Data directory: {paths['data_dir']}")
    print(f"  Plot directory: {paths['plot_dir']}")

    confirm_dirs = input(
        "Do you want to use the default output directories? (y/n): "
    ).strip().lower()
    if confirm_dirs == "n":
        data_dir = input("Enter the path for saving data files: ").strip()
        plot_dir = input("Enter the path for saving plots: ").strip()
    else:
        data_dir = paths["data_dir"]
        plot_dir = paths["plot_dir"]

    ensure_directory(data_dir)
    ensure_directory(plot_dir)

    # Ask for plot preferences
    while True:
        plot_choice = input(
            "Do you want separate plots for 'module_m' and 'epsilon' autocorrelations? (y/n): "
        ).strip().lower()
        if plot_choice in ["y", "n"]:
            separate_plots = plot_choice == "y"
            break
        print("[ERROR] Please answer with 'y' or 'n'.")

    # Confirm inputs
    print("\n===== Summary of Inputs =====")
    print(f"Input Path: {input_path}")
    print(f"Max Lag: {max_lag}")
    print(f"Data Directory: {data_dir}")
    print(f"Plot Directory: {plot_dir}")
    print(f"Separate Plots: {'Yes' if separate_plots else 'No'}")

    confirm = input("\nIs everything correct? (y/n): ").strip().lower()
    if confirm != "y":
        print("Restarting input collection...\n")
        return get_user_inputs(config_path)

    logging.info("All inputs successfully collected.")
    return {
        "input_path": input_path,
        "max_lag": max_lag,
        "data_dir": data_dir,
        "plot_dir": plot_dir,
        "separate_plots": separate_plots,
    }