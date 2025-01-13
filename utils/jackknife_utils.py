import numpy as np
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

def jackknife_means_generation(data):
    """
    Create a Jackknife sample of a dataset.

    Parameters:
    data (numpy.ndarray): 1D array of data points.

    Returns:
    numpy.ndarray: Array of jackknife means.
    """
    n = data.size
    indices = np.arange(n)

    # Create a mask for each jackknife sample by excluding one element at a time
    mask = np.ones((n, n), dtype=bool)
    mask[np.arange(n), indices] = False

    # Create an n x n matrix where each row is a copy of the original data
    data_matrix = np.outer(np.ones(n), data)

    # Use the mask to select N-1 elements for each sample
    jackknife_samples = data_matrix[mask].reshape((n, n-1)) # data must be reshaped, otherwise we obtain a 1D array of len n x (n-1)
    # Compute the mean of each jackknife sample
    jackknife_means = np.mean(jackknife_samples, axis=1)

    return jackknife_means

def binder_var_jk(m_squared, m_fourth):

    m_squared_jk = jackknife_means_generation(m_squared)
    m_fourth_jk = jackknife_means_generation(m_fourth)
    U = m_fourth_jk / m_squared_jk**2
    
    return np.var(U, ddof=1) * (len(U) - 1)

def chi_prime_var_jk(m, m_squared, beta, L, D):

    m_jk = jackknife_means_generation(m)
    m_squared_jk = jackknife_means_generation(m_squared)
    var_m = m_squared_jk - m_jk**2 
    
    chi_prime_var = np.var(var_m, ddof=1) * (len(var_m) - 1) * beta * L**D 
    return chi_prime_var




if __name__=="__main__":

    data = np.random.normal(loc=0., scale=1.0, size=10000)
    data_squared = data**2
    data_fourth = data**4
    
    binder = np.mean(data_fourth) / np.mean(data_squared)**2
    var_U = binder_var_jk(data_squared, data_fourth)
    print(f"U = {binder} +- {np.sqrt(var_U)}")
    
    beta = 1.0; L = 1.0; D = 1.0
    variance = np.mean(data_squared) - np.mean(data)**2
    var_variance = chi_prime_var_jk(data, data_squared, beta, L, D)
    print(f"variance = {variance} +- {np.sqrt(var_variance)}, expected error = {np.sqrt(2 / (len(data)-1))}")
    
    

