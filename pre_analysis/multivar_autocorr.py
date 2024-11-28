import os
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import time
from functools import wraps
import argparse

def timeit(file_path="timing_results.txt"):
    """Decorator to measure the execution time of a function and log it to a file."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            # Write timing result to file
            with open(file_path, "a") as f:
                f.write(f"Tempo impiegato da {func.__name__}: {elapsed_time:.6f} secondi\n")
            return result
        return wrapper
    return decorator
    
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

class TimeSeries_to_autocorr_lag_h:
    def __init__(self, data):
        """
        Initializes the analyzer with the time series data.

        :param data: ndarray of shape (N, n), where N is the number of observations and n is the number of variables.
        """
        # Convert data to float32 for efficiency
        self.data = data.astype(np.float32)
        self.N, self.n = self.data.shape
        self.mean = np.mean(self.data, axis=0)
        self.centered_data = self.data - self.mean  # Center the data by subtracting the mean

        # Compute and store the autocovariance matrix at lag 0
        self.autocov_matrix_0 = self.autocovariance_matrix(h=0)

        # Compute and store the standard deviations and their outer product
        self.variances = np.diag(self.autocov_matrix_0)
        self.stddev = np.sqrt(self.variances)
        self.stddev_matrix = np.outer(self.stddev, self.stddev)
   
    def autocovariance_matrix(self, h=0):
        """
        Calculates the autocovariance matrix at lag h.

        :param h: Time lag.
        :return: Autocovariance matrix of shape (n, n).
        """
        if h >= self.N:
            raise ValueError("The lag h must be less than the number of observations N.")
        T = self.N - h
        data_t = self.centered_data[:T]
        data_t_h = self.centered_data[h:self.N]
        autocov_matrix = np.dot(data_t.T, data_t_h) / T
        return autocov_matrix
    
    def autocorrelation_matrix(self, h=0):
        """
        Calculates the autocorrelation matrix at lag h.

        :param h: Time lag.
        :return: Autocorrelation matrix of shape (n, n).
        """
        autocov_matrix = self.autocovariance_matrix(h)
        autocorr_matrix = autocov_matrix / self.stddev_matrix
        return autocorr_matrix
    
    @timeit('full_lags_autocorr_timing_log.txt')
    def compute_autocorrelations(self, max_lag):
        """
        Computes autocorrelation matrices up to a maximum lag using parallel processing.

        :param max_lag: Maximum lag.
        :return: List of autocorrelation matrices.
        """
        autocorr_matrices = Parallel(n_jobs=-1)(
            delayed(self.autocorrelation_matrix)(h) for h in range(max_lag + 1)
        )
        autocorr_matrices = np.array(autocorr_matrices)
        return autocorr_matrices
    
    def print_to_file(self, filename, max_lag, column_names=None):
        """
        Saves the computed autocorrelation matrices to a file, with an optional header comment.

        :param filename: Name of the output file.
        :param max_lag: Maximum lag for autocorrelations.
        :param column_names: List of column names for the header (optional).
        """
        # Compute the autocorrelation matrices
        autocorr_matrices = self.compute_autocorrelations(max_lag)

        with open(filename, "w") as file:
            # Add column names as a header if provided
            if column_names:
                header = "# Columns: " + ", ".join(column_names) + "\n"
                file.write(header)

            # Save each matrix as a flattened row with the lag as the first value
            for matrix in autocorr_matrices:
                flattened_matrix = matrix.flatten()
                np.savetxt(file, [flattened_matrix], fmt='%0.12f', delimiter=" ")
        return

if __name__ == '__main__':
    # Section to deal with command lines from terminal
    parser = argparse.ArgumentParser(description="Program to compute autocorrelation for a set of files in a folder")
    parser.add_argument("--import_path", type=str, required=True,
            help="Folder in which all the files are stored")
    parser.add_argument("--export_path", type=str, default="export_path/",
            help="Folder in which all the computed autocorrelations will be stored")
    parser.add_argument("--max_lag", type=int, required=True,
            help="Max autocorrelation lag")
    args = parser.parse_args()
    import_path = args.import_path
    export_path = args.export_path
    current_max_lag = args.max_lag
    os.makedirs(export_path, exist_ok=True)

    for file_name in os.listdir(import_path):
        file_path = os.path.join(import_path, file_name)
        # Check if it has a .dat or .bin extension
        if file_name.endswith(('.dat', '.bin')):
            base_name, ext = os.path.splitext(file_name) # split filename from its extension
            output_file = os.path.join(
                    export_path, base_name + '_autocorr.txt'
            )
            data = load_binary_file(file_path, 3)
            magns_per_site = data[:,:2]
            analyzer = TimeSeries_to_autocorr_lag_h(magns_per_site)
            analyzer.print_to_file(output_file, current_max_lag, 
                    column_names=["autocorr_XX", "autocorr_XY", "autocorr_YX", "autocorr_YY"])

