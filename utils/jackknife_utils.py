import os
import numpy as np
import pandas as pd
from multiprocessing import Pool
from io_utils import ensure_directory, extract_lattice_side, extract_beta
from interface_utils import navigate_directories

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
    var_m = m_squared_jk - m_jk**2 
    
    chi_prime_var = np.var(var_m, ddof=1) * (len(var_m) - 1) * beta * L**D 
    return chi_prime_var

def perform_jackknife_blocking(input_paths, output_dir, first_index, num_cores, max_block_size):
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

if __name__=="__main__":
    input_paths = navigate_directories(start_path=".", multi_select=True, file_extension=".csv")
    output_dir = "./output"
    first_index = 5000
    num_cores = 4
    max_block_size = 100

    perform_jackknife_blocking(input_paths, output_dir, first_index, num_cores, max_block_size)
