import os
import logging
from io_utils import load_config, ensure_directory



def navigate_directories(start_path=".", multi_select=False, file_extension=".bin"):
    """
    Allows users to navigate directories and select files or folders.

    Parameters:
        start_path (str): The starting directory for navigation.
        multi_select (bool): If True, allows selection of multiple files or folders.
        file_extension (str): File extension to filter files (e.g., '.bin').

    Returns:
        list[str]: List of selected file or folder paths.
    """
    current_dir = os.path.abspath(start_path)
    selected_paths = []

    while True:
        # Filter and sort contents (exclude hidden files/directories)
        contents = [item for item in sorted(os.listdir(current_dir)) if not item.startswith('.')]
        directories = [item for item in contents if os.path.isdir(os.path.join(current_dir, item))]
        files = [item for item in contents if os.path.isfile(os.path.join(current_dir, item)) and item.endswith(file_extension)]

        # Display current directory and contents
        print(f"\nCurrent directory: {current_dir}")
        print("Directories:")
        for idx, directory in enumerate(directories, 1):
            print(f"  D{idx}. {directory}")
        print("Files:")
        for idx, file in enumerate(files, len(directories) + 1):
            print(f"  F{idx}. {file}")

        # Display actions
        print("\nActions: '..' (up), '.' (list), 'done' (finish selection), 'exit' (quit), 'all' (select all)")

        user_input = input("Enter your choice (number, '..', '.', 'done', 'exit', 'all'): ").strip()

        if user_input == "exit":
            print("[INFO] Exiting navigation.")
            exit(0)
        elif user_input == "done":
            if selected_paths:
                break
            print("[INFO] No selections made. Returning to navigation.")
        elif user_input == "..":
            # Move up one directory
            current_dir = os.path.dirname(current_dir)
        elif user_input == ".":
            # Refresh listing
            continue
        elif user_input == "all":
            # Select all visible items
            for item in contents:
                item_path = os.path.join(current_dir, item)
                if os.path.isdir(item_path):
                    # Recursively collect files from directory
                    for root, _, files_in_dir in os.walk(item_path):
                        selected_paths.extend([os.path.join(root, f) for f in files_in_dir if f.endswith(file_extension)])
                elif os.path.isfile(item_path) and item_path.endswith(file_extension):
                    selected_paths.append(item_path)
            print(f"[INFO] Selected all items: {selected_paths}")
            break
        elif user_input.startswith("D") and user_input[1:].isdigit():
            # Handle directory selection
            choice_idx = int(user_input[1:]) - 1
            if 0 <= choice_idx < len(directories):
                current_dir = os.path.join(current_dir, directories[choice_idx])
            else:
                print("[ERROR] Invalid directory index.")
        elif user_input.startswith("F") and user_input[1:].isdigit():
            # Handle file selection
            choice_idx = int(user_input[1:]) - 1 - len(directories)
            if 0 <= choice_idx < len(files):
                selected_path = os.path.join(current_dir, files[choice_idx])
                if multi_select:
                    if selected_path not in selected_paths:
                        selected_paths.append(selected_path)
                        print(f"[INFO] Added to selection: {selected_path}")
                    else:
                        print("[INFO] File already selected.")
                else:
                    return [selected_path]
            else:
                print("[ERROR] Invalid file index.")
        else:
            print("[ERROR] Invalid command.")

    return selected_paths



def get_user_inputs_for_mcmc_termalization_analysys(config_path="../configs/mcmc_termalization_config.yaml"):
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
    default_files = paths.get("default_files", [])

    print("\n===== MCMC Autocorrelation Analysis =====\n")

    input_paths = []

    # Option to choose from default files
    if default_files:
        print("Default Files:")
        for idx, file_path in enumerate(default_files, start=1):
            print(f"  {idx}. {file_path}")
        print("  0. None of these (manual entry or navigate)")

        while True:
            default_choice = input("\nSelect file(s) from the list (e.g., '1 2 3' or 'all', or 0 to skip): ").strip()
            if default_choice == "0":
                input_paths = []
                break
            elif default_choice.lower() == "all":
                input_paths = default_files
                print(f"[INFO] Selected all default files.")
                break
            else:
                try:
                    selected_indices = list(map(int, default_choice.split()))
                    if all(1 <= idx <= len(default_files) for idx in selected_indices):
                        input_paths = [default_files[idx - 1] for idx in selected_indices]
                        print(f"[INFO] Selected files: {input_paths}")
                        break
                except ValueError:
                    pass
                print("[ERROR] Invalid choice. Please try again.")

    # Option to manually enter a path
    if not input_paths:
        manual_path = input("\nEnter a file or folder path (leave empty to navigate): ").strip()
        if manual_path:
            if os.path.exists(manual_path):
                if os.path.isdir(manual_path):
                    # Collect all .bin and .dat files in the directory and subdirectories
                    input_paths = [
                        os.path.join(root, f)
                        for root, _, files in os.walk(manual_path)
                        for f in files if f.endswith(('.bin', '.dat'))
                    ]
                    print(f"[INFO] Selected all valid files in the directory and subdirectories: {input_paths}")
                elif os.path.isfile(manual_path):
                    input_paths = [manual_path]
            else:
                print("[ERROR] Path does not exist. Please try again.")
                return get_user_inputs(config_path)

    # Navigate directories if no path is specified
    if not input_paths:
        print("\nNavigate to select the input file(s) or folder(s).")
        input_paths = navigate_directories(start_path=".", multi_select=True, file_extension=".bin")
        if not input_paths:
            print("[INFO] No files selected. Exiting...")
            exit(0)

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

    # Use x_scale and y_scale from configuration
    x_scale = defaults["x_scale"]
    y_scale = defaults["y_scale"]

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
    print(f"Input Paths: {input_paths}")
    print(f"Max Lag: {max_lag}")
    print(f"Data Directory: {data_dir}")
    print(f"Plot Directory: {plot_dir}")
    print(f"Separate Plots: {'Yes' if separate_plots else 'No'}")
    print(f"x_scale: {x_scale}")
    print(f"y_scale: {y_scale}")

    confirm = input("\nIs everything correct? (y/n): ").strip().lower()
    if confirm != "y":
        print("Restarting input collection...\n")
        return get_user_inputs(config_path)

    logging.info("All inputs successfully collected.")
    return {
        "input_paths": input_paths,
        "max_lag": max_lag,
        "data_dir": data_dir,
        "plot_dir": plot_dir,
        "separate_plots": separate_plots,
        "x_scale": x_scale,
        "y_scale": y_scale,
    }
    





def get_user_inputs_for_blocking_analysis(config_path="../configs/blocking_config.yaml"):
    """
    Interactive interface to ask the user for inputs specific to blocking analysis.

    Parameters:
        config_path (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing all user inputs and preferences.
    """
    # Load configuration values
    config = load_config(config_path)
    defaults = config["settings"]
    paths = config["paths"]
    default_files = paths.get("default_files", [])

    print("\n===== Blocking Analysis =====\n")

    input_paths = []

    # Option to choose from default files
    if default_files:
        print("Default Files:")
        for idx, file_path in enumerate(default_files, start=1):
            print(f"  {idx}. {file_path}")
        print("  0. None of these (manual entry or navigate)")

        while True:
            default_choice = input("\nSelect file(s) from the list (e.g., '1 2 3' or 'all', or 0 to skip): ").strip()
            if default_choice == "0":
                input_paths = []
                break
            elif default_choice.lower() == "all":
                input_paths = default_files
                print(f"[INFO] Selected all default files.")
                break
            else:
                try:
                    selected_indices = list(map(int, default_choice.split()))
                    if all(1 <= idx <= len(default_files) for idx in selected_indices):
                        input_paths = [default_files[idx - 1] for idx in selected_indices]
                        print(f"[INFO] Selected files: {input_paths}")
                        break
                except ValueError:
                    pass
                print("[ERROR] Invalid choice. Please try again.")

    # Option to manually enter a path
    if not input_paths:
        manual_path = input("\nEnter a file or folder path (leave empty to navigate): ").strip()
        if manual_path:
            if os.path.exists(manual_path):
                if os.path.isdir(manual_path):
                    # Collect all .bin and .dat files in the directory and subdirectories
                    input_paths = [
                        os.path.join(root, f)
                        for root, _, files in os.walk(manual_path)
                        for f in files if f.endswith(('.bin', '.dat'))
                    ]
                    print(f"[INFO] Selected all valid files in the directory and subdirectories: {input_paths}")
                elif os.path.isfile(manual_path):
                    input_paths = [manual_path]
            else:
                print("[ERROR] Path does not exist. Please try again.")
                return get_user_inputs_for_blocking_analysis(config_path)

    # Navigate directories if no path is specified
    if not input_paths:
        print("\nNavigate to select the input file(s) or folder(s).")
        input_paths = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")
        if not input_paths:
            print("[INFO] No files selected. Exiting...")
            exit(0)

    # Ask for maximum block size
    max_block_size_default = defaults.get("max_block_size_default", None)
    while True:
        max_block_size_input = input(
            f"\nEnter the maximum block size (Default: {max_block_size_default}): "
        ).strip()
        if not max_block_size_input:
            max_block_size = max_block_size_default
            break
        try:
            max_block_size = int(max_block_size_input)
            break
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")

    # Ask for number of cores
    num_cores_default = defaults.get("num_cores_default", None)
    while True:
        num_cores_input = input(
            f"\nEnter the number of cores to use (Default: {num_cores_default}): "
        ).strip()
        if not num_cores_input:
            num_cores = num_cores_default
            break
        try:
            num_cores = int(num_cores_input)
            break
        except ValueError:
            print("[ERROR] Invalid input. Please enter a number.")

    # Ask for data output directory
    print("\nData Directory for CSV outputs:")
    print(f"  Default: {paths['data_dir']}")
    data_dir = input("Enter the data directory path (leave empty to use default): ").strip()
    if not data_dir:
        data_dir = paths["data_dir"]
    ensure_directory(data_dir)
    
    # Ask for plot output directory
    print("\nPlot Directory:")
    print(f"  Default: {paths['plot_dir']}")
    plot_dir = input("Enter the plot directory path (leave empty to use default): ").strip()
    if not plot_dir:
        plot_dir = paths["plot_dir"]
    ensure_directory(plot_dir)

    # Confirm inputs
    print("\n===== Summary of Inputs =====")
    print(f"Input Paths: {input_paths}")
    print(f"Max Block Size: {max_block_size}")
    print(f"Number of Cores: {num_cores}")
    print(f"Data output directory: {data_dir}")
    print(f"Data output directory: {plot_dir}")

    confirm = input("\nIs everything correct? (y/n): ").strip().lower()
    if confirm != "y":
        print("Restarting input collection...\n")
        return get_user_inputs_for_blocking_analysis(config_path)

    # Return collected inputs as a dictionary
    return {
        "input_paths": input_paths,
        "max_block_size": max_block_size,
        "num_cores": num_cores,
        "data_dir": data_dir,
        "plot_dir": plot_dir,
    }







def get_user_inputs_for_saving_lattice_metrics_to_csv(config_path="configs/lattice_metrics_to_csv_config.yaml"):
    """
    Interactive interface to gather user inputs for the analysis task.

    Parameters:
        config_path (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing user-provided input paths and directories.
    """
    # Load configuration
    config = load_config(config_path)
    paths = config["paths"]
    default_files = paths.get("default_files", [])
    output_dir_default = paths.get("output_dir", "./results")
    index_threshold = config["settings"].get("index_threshold")

    print("\n===== Analysis Configuration =====\n")

    # Select input files
    input_paths = []
    if default_files:
        print("Default Files:")
        for idx, file_path in enumerate(default_files, start=1):
            print(f"  {idx}. {file_path}")
        print("  0. None (enter manually or navigate)")

        while True:
            choice = input("Choose files by number (e.g., '1 2') or '0' to skip: ").strip()
            if choice == "0":
                break
            elif choice.lower() == "all":
                input_paths = default_files
                break
            else:
                try:
                    indices = list(map(int, choice.split()))
                    if all(1 <= i <= len(default_files) for i in indices):
                        input_paths = [default_files[i - 1] for i in indices]
                        break
                except ValueError:
                    print("[ERROR] Invalid choice. Try again.")
    
    if not input_paths:
        print("\nNavigate to select input files.")
        input_paths = navigate_directories(multi_select=True, file_extension=".bin")
        if not input_paths:
            print("[INFO] No files selected. Exiting...")
            sys.exit(0)

    # Select output directory
    print("\nOutput Directory:")
    print(f"Default: {output_dir_default}")
    output_dir = input("Enter output directory or press Enter for default: ").strip()
    if not output_dir:
        output_dir = output_dir_default
    ensure_directory(output_dir)

    return {
        "input_paths": input_paths,
        "output_dir": output_dir,
        "index_threshold": index_threshold,
    }



def get_user_inputs_for_principal_quantities_means(config_path="..configs/lattices_means_to_csv_config.yaml"):
    """
    Interactive interface to gather user inputs for summarizing CSV files.

    Parameters:
        config_path (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing user-provided input paths and output configurations.
    """
    # Load configuration
    config = load_config(config_path)
    paths = config.get("paths", {})
    
    # Default values from the configuration file
    input_dir_default = paths.get("input_dir", "./data/lattice_metrics_csv")
    output_dir_default = paths.get("output_dir", "./data/summary_metrics")
    output_file_default = paths.get("output_file", "lattice_means_summary.csv")
    
    print("\n===== Summary Analysis Configuration =====\n")

    # Prompt for input directory
    print(f"Input Directory (Default: {input_dir_default}):")
    input_dir = input("Enter input directory or press Enter to use the default: ").strip()
    if not input_dir:
        input_dir = input_dir_default

    # Prompt for output directory
    print(f"Output Directory (Default: {output_dir_default}):")
    output_dir = input("Enter output directory or press Enter to use the default: ").strip()
    if not output_dir:
        output_dir = output_dir_default

    # Prompt for output file name
    print(f"Output File Name (Default: {output_file_default}):")
    output_file = input("Enter output file name or press Enter to use the default: ").strip()
    if not output_file:
        output_file = output_file_default

    # Ensure output directory exists
    ensure_directory(output_dir)

    print("\n===== Summary of Inputs =====")
    print(f"Input Directory: {input_dir}")
    print(f"Output Directory: {output_dir}")
    print(f"Output File Name: {output_file}")

    confirm = input("\nIs everything correct? (y/n): ").strip().lower()
    if confirm != "y":
        print("\nRestarting input collection...")
        return get_user_inputs_for_principal_quantities_means(config_path)

    return {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "output_file": output_file,
    }

def get_user_inputs_for_jackknife(config):
    """Update the configuration based on user input."""
    # Prompt user for 'first_index' with a default value
    first_index_input = input(f"Enter first index (default: {config['settings']['first_index']}): ").strip()
    config['settings']['first_index'] = int(first_index_input) if first_index_input else config['settings']['first_index']

    # Prompt user for 'max_block_size_default' with a default value
    max_block_size_input = input(f"Enter max block size (default: {config['settings']['max_block_size_default']}): ").strip()
    config['settings']['max_block_size_default'] = int(max_block_size_input) if max_block_size_input else config['settings']['max_block_size_default']

    # Prompt user for 'num_cores_default' with a default value
    num_cores_input = input(f"Enter number of cores (default: {config['settings']['num_cores_default']}): ").strip()
    config['settings']['num_cores_default'] = int(num_cores_input) if num_cores_input else config['settings']['num_cores_default']

    # Prompt user for 'single_block_size_default' with a default value
    single_block_size_input = input(f"Enter single block size (default: {config['settings']['single_block_size_default']}): ").strip()
    config['settings']['single_block_size_default'] = int(single_block_size_input) if single_block_size_input else config['settings']['single_block_size_default']

    # Prompt user for 'data_columns' with a default value
    data_columns_input = input(f"Enter data columns as comma-separated values (default: {','.join(config['settings']['data_columns'])}): ").strip()
    config['settings']['data_columns'] = data_columns_input.split(',') if data_columns_input else config['settings']['data_columns']

    # Prompt user for directory paths with default values
    config['paths']['output_dir'] = input(f"Enter output data directory (default: {config['paths']['output_dir']}): ").strip() or config['paths']['output_dir']
    config['paths']['plot_dir'] = input(f"Enter plot directory (default: {config['paths']['plot_dir']}): ").strip() or config['paths']['plot_dir']

    # Optionally update input paths
    logging.info("======== Selection of files for MAX blocking + jackknife analysis ========")
    config['paths']['default_files_4_maxblock_analysis'] = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")
    logging.info("======== Selection of files for SINGLE blocking + jackknife analysis ========")
    config['paths']['default_files_4_singleblock_analysis'] = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")

    return config
