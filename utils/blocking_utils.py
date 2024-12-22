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

