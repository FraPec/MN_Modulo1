import os
import numpy as np
import pandas as pd
import logging
from multiprocessing import Pool
from io_utils import prompt_user_choice, load_config, ensure_directory, extract_lattice_side, extract_beta
from interface_utils import navigate_directories
from plot_utils import plot_jackknife_blocking_variance

def blocking_data(data, block_size):
    """
    Perform blocking analysis for a given block size, optimized for efficiency.

    Parameters:
        data (np.ndarray): Input data to analyze.
        block_size (int): Size of each block.

    Returns:
        block_means (np.ndarray): blocked data of len N//block_size
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
    
    return block_means

def blocking_data_parallel(data, max_block_size, num_cores=None):
    """
    Perform blocking for jackknife for all block sizes up to max_block_size using parallel processing.
    """

    with Pool(processes=num_cores) as pool:
        block_sizes = np.arange(1, max_block_size + 1)
        blocked_data = pool.starmap(blocking_data, [(data, bs) for bs in block_sizes])
    return block_sizes, blocked_data

def jackknife_means_generation(data):
    """
    Create a Jackknife sample of a dataset in a memory-efficient way.

    Parameters:
    data (numpy.ndarray): 1D array of data points.

    Returns:
    numpy.ndarray: Array of jackknife means.
    """
    n = data.size
    jackknife_means = np.empty(n)
    total_sum = np.sum(data)
    
    for i in range(n):
        # Calculate the sum of data excluding the i-th element
        jackknife_sum = total_sum - data[i]
        # Calculate the mean excluding the i-th element
        jackknife_means[i] = jackknife_sum / (n - 1)
    
    return jackknife_means


def binder_var_jk(m_squared, m_fourth):
    """
    Compute the variance for the Binder cumulant, U = <m^4> / <m^2>^2 .

    Parameters:
        m_squared (numpy.ndarray): 1D array of the dataset to the second power
        m_fourth (numpy.ndarray): 1D array of the dataset to the fourth power

    Returns:
        var_U (float): variance of Binder cumulant
    """
    m_squared_jk = jackknife_means_generation(m_squared)
    m_fourth_jk = jackknife_means_generation(m_fourth)
    U = m_fourth_jk / m_squared_jk**2
    var_U = np.var(U, ddof=1) * (len(U) - 1) 
    return var_U

def chi_prime_var_jk(m, m_squared, beta, L, D):
    """
    Compute the variance for the Chi prime = beta * L^D * (<m^2> - <m>^2).

    Parameters:
        m (numpy.ndarray): 1D array of the dataset
        m_squared (numpy.ndarray): 1D array of the dataset to the second power
        beta (float): reciprocal of the temperature
        L (int): lattice size
        D (int): dimensionality

    Returns:
        var_U (float): variance of Binder cumulant
    """
    m_jk = jackknife_means_generation(m)
    m_squared_jk = jackknife_means_generation(m_squared)
    chi_prime = (m_squared_jk - m_jk**2) * beta * L**D
    
    chi_prime_var = np.var(chi_prime, ddof=1) * (len(chi_prime) - 1) 
    return chi_prime_var

def perform_jackknife_blocking_analysis(input_paths, output_dir, first_index, num_cores, max_block_size):
    """
    Performs data analysis on input files and saves the results.

    This function reads data from specified input paths, processes the data using 
    blocking analysis, calculates variances for chi prime and the Binder cumulant 
    using jackknife resampling, and saves the processed data to output files.

    Parameters:
        input_paths (list of str): List of file paths to the input CSV files. Each file 
                                   should contain columns for 'L', 'beta', 'absm', 'm2', and 'm4'.
        output_dir (str): Directory where the output files will be saved. A subdirectory 
                          is created for each lattice size.
        first_index (int): Index to start reading the data from each input file, allowing 
                           for skipping initial rows (e.g., for equilibration).
        num_cores (int): Number of CPU cores to use for parallel processing in the 
                         blocking analysis.
        max_block_size (int): Maximum block size to use in the blocking analysis.

    Returns:
        None
    """
    D = 3
    columns_to_process = ["L", "beta", "absm", "m2", "m4"]
    df_list = []
    lattice_list = []
    beta_list = []

    for path in input_paths:
        df = pd.read_csv(path)[columns_to_process][first_index:]
        df_list.append(df)
        lattice_list.append(df["L"].iloc[0])
        beta_list.append(df["beta"].iloc[0])
    
    total_files_to_process = len(df_list)
    processed_files = 1
    for L, beta, df in zip(lattice_list, beta_list, df_list):
        absm, m2, m4 = df["absm"].values, df["m2"].values, df["m4"].values
        block_sizes, absm_blocked = blocking_data_parallel(absm, max_block_size, num_cores=num_cores)
        m2_blocked = blocking_data_parallel(m2, max_block_size, num_cores=num_cores)[1]
        m4_blocked = blocking_data_parallel(m4, max_block_size, num_cores=num_cores)[1]

        var_chi_prime = []
        var_U = []
        for absm_blk, m2_blk, m4_blk in zip(absm_blocked, m2_blocked, m4_blocked):
            var_U.append(binder_var_jk(m2_blk, m4_blk))
            var_chi_prime.append(chi_prime_var_jk(absm_blk, m2_blk, beta, L, D))

        output_df = pd.DataFrame({
            'block_size': block_sizes,
            'L': L,
            'beta': beta,
            'var_chi_prime': var_chi_prime,
            'var_U': var_U
        })
        
        subfolder = os.path.join(output_dir, f'L{L}')
        ensure_directory(subfolder)
        output_path = os.path.join(subfolder, f'data_L{L}_{beta}_jackknife_blocking.csv')
        output_df.to_csv(output_path, index=False)
        logging.info(f"Blocking + JK analysis: processed and saved lattice {L} with beta {beta}, {processed_files}/{total_files_to_process}.\n")
        processed_files += 1

def perform_jackknife_blocking(input_paths, output_dir, first_index, num_cores, block_size):
    """
    Performs jackknife + blocking for all the file selected, JUST for the chosen blocksize

    This function reads data from specified input paths, processes the data using 
    blocking, calculates variances for chi prime and the Binder cumulant using 
    jackknife resampling, and saves the processed data to 2 output files, one for 
    the means and one for the variances.

    Parameters:
        input_paths (list of str): List of file paths to the input CSV files. Each file 
                                   should contain columns for 'L', 'beta', 'absm', 'm2', and 'm4'.
        output_dir (str): Directory where the output files will be saved.
        first_index (int): Index to start reading the data from each input file, allowing 
                           for skipping initial rows (e.g., for equilibration).
        num_cores (int): Number of CPU cores to use for parallel processing in the 
                         blocking analysis.
        block_size (int): Block size chosen to use in the blocking analysis.

    Returns:
        None
    """
    D = 3
    columns_to_process = ["L", "beta", "absm", "m2", "m4"]
    df_list = []
    lattice_list = []
    beta_list = []

    chi_prime_mean = []
    var_chi_prime = []
    U_mean = []
    var_U = []

    total_files_to_process = len(input_paths)
    processed_files = 1
    
    for path in input_paths:
        df = pd.read_csv(path)[columns_to_process][first_index:]
        df_list.append(df)
        L = df["L"].iloc[0]
        beta = df["beta"].iloc[0]
        lattice_list.append(L)
        beta_list.append(beta)
   
        absm, m2, m4 = df["absm"].values, df["m2"].values, df["m4"].values

        absm_blocked = blocking_data(absm, block_size)
        m2_blocked = blocking_data(m2, block_size)
        m4_blocked = blocking_data(m4, block_size)
        
        chi_prime_mean.append((np.mean(m2) - np.mean(absm)**2) * beta * L**D)
        var_chi_prime.append(chi_prime_var_jk(absm_blocked, m2_blocked, beta, L, D))
        U_mean.append(np.mean(m4) / np.mean(m2)**2)
        var_U.append(binder_var_jk(m2_blocked, m4_blocked))

        logging.info(f"Loaded and processed lattice {L} with beta {beta}, {processed_files}/{total_files_to_process}.\n")
        processed_files += 1
 

    df_vars = pd.DataFrame({
        'L': lattice_list,
        'beta': beta_list,
        'var_chi_prime': var_chi_prime,
        'var_U': var_U
    })

    ensure_directory(output_dir)
    output_path = os.path.join(output_dir, f'secondary_quantities_variances.csv')
    df_vars.to_csv(output_path, index=False)
    
    df_means = pd.DataFrame({
        'L': lattice_list,
        'beta': beta_list,
        'chi_prime_mean': chi_prime_mean,
        'U_mean': U_mean
    })

    output_path = os.path.join(output_dir, f'secondary_quantities_means.csv')
    df_means.to_csv(output_path, index=False)



def plot_jackknife_variances(df, plot_dir, base_name):
    """Generate and save plots for the variance data."""
    blocksizes = df["block_size"]
    
    # Plot for variance of U
    var_U = df["var_U"]
    save_path = os.path.join(plot_dir, f"{base_name}_var_U.png")
    plot_jackknife_blocking_variance(var_U, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance")

    # Plot for variance of chi prime
    var_chi_prime = df["var_chi_prime"]
    save_path = os.path.join(plot_dir, f"{base_name}_var_chi_prime.png")
    plot_jackknife_blocking_variance(var_chi_prime, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance")


