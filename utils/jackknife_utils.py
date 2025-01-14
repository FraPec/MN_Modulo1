from time import time
import numpy as np
from multiprocessing import Pool
from io_utils import ensure_directory, extract_lattice_side, extract_beta

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
        block_sizes = range(1, max_block_size + 1)
        blocked_data = pool.starmap(blocking_data, [(data, bs) for bs in block_sizes])
    return dict(zip(block_sizes, blocked_data))

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


if __name__=="__main__":

    data = np.random.normal(loc=0., scale=1.0, size=1000000)
    data_squared = data**2
    data_fourth = data**4
    
    t0 = time()
    num_cores = 1
    blocked_data_dic = blocking_data_parallel(data, 5000, num_cores=num_cores)
    blocked_data_squared_dic = blocking_data_parallel(data_squared, 5000, num_cores=num_cores)
    blocked_data_fourth_dic = blocking_data_parallel(data_fourth, 5000, num_cores=num_cores)
    print(f"time: {time()-t0}s")


    blocked_data = blocked_data_dic[1]
    blocked_data_squared = blocked_data_squared_dic[1]
    blocked_data_fourth = blocked_data_fourth_dic[1]

    binder = np.mean(data_fourth) / np.mean(data_squared)**2
    var_U = binder_var_jk(blocked_data_squared, blocked_data_fourth)
    print(f"U = {binder} +- {np.sqrt(var_U)}")
    
    beta = 1.0; L = 1.0; D = 1.0
    variance = np.mean(data_squared) - np.mean(data)**2
    var_variance = chi_prime_var_jk(blocked_data, blocked_data_squared, beta, L, D)
    print(f"variance = {variance} +- {np.sqrt(var_variance)}, expected error = {np.sqrt(2 / (len(data)-1))}")
    
    

