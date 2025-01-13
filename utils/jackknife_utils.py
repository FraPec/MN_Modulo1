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

def jackknife_sample_generation(data):
    """
    Perform jackknife resampling on a dataset.

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

    print(mask)

    # Create an n x n matrix where each row is a copy of the original data
    data_matrix = np.outer(np.ones(n), data)
    
    print(data_matrix)

    # Use the mask to select N-1 elements for each sample
    jackknife_samples = data_matrix[mask].reshape((n, n-1))

    print(jackknife_samples)

    # Compute the mean of each jackknife sample
    jackknife_means = np.mean(jackknife_samples, axis=1)
    
    print(jackknife_means)
    return jackknife_means


if __name__=="__main__":

    data = np.linspace(0,100, 101)

    blocked_data = blocking_data(data, 11)
    print(data)
    print(blocked_data)

    print("jackknife procedure...\n\n")
    jackknife_sample = jackknife_sample_generation(blocked_data)


