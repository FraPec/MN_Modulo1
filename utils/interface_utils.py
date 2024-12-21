import os
from io_utils import load_config



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


def get_user_inputs_for_mcmc_termalization_analysys(config_path="mcmc_termalization_config.yaml"):
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
    



