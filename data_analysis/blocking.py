from scipy.optimize import curve_fit
from scipy.stats import linregress 
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt
import argparse

def load_binary_file(filepath, n_cols):
    """
    Loads a binary file containing three columns of float64 data into a 2D NumPy array.

    :param filepath: Path to the binary file.
    :return: A NumPy array of shape (N, n_cols), where N is the number of rows.
    """
    # Load the binary data as a 1D array of float64
    data = np.fromfile(filepath, dtype=np.float64)

    # Reshape the data into a 2D array with three columns
    if data.size % n_cols != 0:
        raise ValueError(f"The file size is not a multiple of {n_cols}, suggesting data corruption or an incorrect file format.")

    data = data.reshape(-1, n_cols)  # Reshape to have 3 columns
    return data

def blocking(data, block_size):
    N = data.shape[0]
    data = data[:(N//block_size * block_size)]
    data_reshaped = data.reshape(N//block_size, block_size)
    data_k = np.mean(data_reshaped, axis = 1) # mean over the block of len block_size
    data_mean = np.mean(data)
    data_res_k = data_k - data_mean
    variance = 1 / ((N/block_size) * (N/block_size - 1)) * np.sum(np.power(data_res_k, 2))
    return variance

if __name__ == "__main__":
    # Section to deal with command lines from terminal
    parser = argparse.ArgumentParser(description="Fit and plot to estimate the std dev for the sample means")
    parser.add_argument("--input_datafile", type=str,required=True, 
            help="Name of the input data file to analize with blocking")
    parser.add_argument("--output_datafile", type=str,required=True, 
            help="Name of the output data file in which we print the blocked variances")
    args = parser.parse_args()
    data_filename = args.input_datafile
    filename = args.output_datafile
    
    # Load and preprocess data
    data = load_binary_file(data_filename, 3)
    data = data[int(5e3):, :]
    N = data.shape[0]
    print(data.shape)
    # Generate a list of all the variables to compute
    module = np.linalg.norm(data[:, :2], axis=1) # |m|
    
    data_arrays = np.array([data[:, 0], data[:, 1], data[:, 2], # mx, my, E 
            module, # |m|
            np.power(module, 2.0), # |m|^2
            np.power(module, 4.0) # |m|^4
            ]).T
    print(data_arrays.shape)

    # Check that everything went fine with modules 
    module_to_compare = np.sqrt(np.power(data_arrays[:, 0], 2.0) + np.power(data_arrays[:, 1], 2.0))
    if np.all(np.isclose(module_to_compare, data_arrays[:, 3])):
        print("module is ok")
    else:
        raise ValueError("Something wrong happened with modules")
    if np.all(np.isclose(module_to_compare, np.sqrt(data_arrays[:, 4]))):
        print("module squared is ok")
    else:
        raise ValueError("Something wrong happened with squared modules")
    if np.all(np.isclose(module_to_compare, np.power(data_arrays[:, 5], 1.0/4.0))):
        print("module to the forth power is ok")
    else:
        raise ValueError("Something wrong happened with modules to the fourth power")

    # Generate block sizes
    block_sizes_v = np.unique(np.logspace(0, np.log10(N/2), 400, dtype=int))
    variances_from_blocking = np.zeros((block_sizes_v.shape[0], data_arrays.shape[1]))

    means = []
    for index in range(data_arrays.shape[1]):
        # Compute mean
        mean = np.mean(data_arrays[:, index])
        means.append(mean)

        # Compute standard deviation for each block size
        for i, block_size in enumerate(block_sizes_v):
            variances_from_blocking[i, index] = blocking(data_arrays[:, index], block_size)

    means = [0.] + means
    means = np.array(means)
    means = means[np.newaxis, :]
    variances_from_blocking = np.hstack((block_sizes_v[:, np.newaxis], variances_from_blocking))
    array_to_save = np.vstack((means, variances_from_blocking))
    np.savetxt(filename, array_to_save, 
            header="var_mx, var_my, var_E, var_|m|, var_|m|^2, var_|m|^4\nFirst line has the 6 means of the values")

