import numpy as np
import os
from multiprocessing import Pool
from io_utils import ensure_directory

def blocking(data, block_size):
    """
    Perform blocking analysis for a given block size, optimized for efficiency.

    Parameters:
        data (np.ndarray): Input data to analyze.
        block_size (int): Size of each block.

    Returns:
        float: Variance calculated for the given block size.
    """
    # Number of blocks
    n_blocks = len(data) // block_size
    
    # Ensure there are enough blocks to calculate variance
    if n_blocks <= 1:
        raise ValueError("Block size too large for the dataset.")
    
    # Truncate data to make it divisible by block_size
    truncated_data = data[:n_blocks * block_size]
    
    # Reshape data into blocks and calculate block means
    reshaped_data = truncated_data.reshape(n_blocks, block_size)
    block_means = reshaped_data.mean(axis=1)
    
    # Calculate the global mean of the original data
    global_mean = truncated_data.mean()
    
    # Variance calculation
    deviations_squared = (block_means - global_mean) ** 2
    variance = deviations_squared.sum() / (n_blocks * (n_blocks - 1))
    
    return variance
    
    

def calculate_blocking_variances(data, max_block_size, num_cores=None):
    """
    Calculate variances for all block sizes up to max_block_size using parallel processing.
    """

    with Pool(processes=num_cores) as pool:
        block_sizes = range(1, max_block_size + 1)
        results = pool.starmap(blocking, [(data, bs) for bs in block_sizes])
    return dict(zip(block_sizes, results))



def check_existing_blocking_files(blocking_csv, plot_files):
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
    user_choices = check_existing_blocking_files(blocking_csv, plot_files)
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
    



