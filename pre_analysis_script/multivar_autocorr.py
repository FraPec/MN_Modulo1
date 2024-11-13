import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import time
from functools import wraps



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

    
    
    @timeit('single_lag_autocorr_timing_log.txt')
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




if __name__ == '__main__':
    
    #Importing data from binary file
    data = load_binary_file('MN_Modulo1/pre_analysis_data/data/lattice10/data_b0.5_a0.001_L10.dat', 3)
    magns_per_site = data[:,0:2]
    e_per_site = data[:,2]
    # Make a class instance 
    analyzer = TimeSeries_to_autocorr_lag_h(magns_per_site)
    #Compute the autocorr of lag h of the multivariate time series
    autocorr_matrices = analyzer.compute_autocorrelations(max_lag = int(analyzer.N / 2))
    
    print(autocorr_matrices[1])
    
    
    
    

