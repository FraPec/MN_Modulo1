import numpy as np
from joblib import Parallel, delayed

def center_data(data):
    """Center data by subtracting the mean."""
    return data - np.mean(data, axis=0)



def compute_autocovariances(data, max_lag):
    """
    Computes the autocovariance matrix up to max_lag for a 2D input data.

    Parameters:
        data (np.ndarray): Input data array with shape (n, 2).
        max_lag (int): Maximum lag for autocovariance computation.

    Returns:
        np.ndarray: A 3D NumPy array with shape (max_lag+1, 2, 2),
                    where each slice is the autocovariance matrix for a given lag.
    """
    n_samples, n_features = data.shape
    autocov_matrices = []

    # Mean-center the data
    data_centered = data - np.mean(data, axis=0)

    for lag in range(max_lag + 1):
        if lag == 0:
            cov_matrix = np.cov(data_centered.T, bias=True)  # Lag 0 covariance
        else:
            cov_matrix = np.dot(
                data_centered[:-lag].T, data_centered[lag:]
            ) / (n_samples - lag)  # Autocovariance at lag h
        autocov_matrices.append(cov_matrix)

    return np.array(autocov_matrices)
    
    

def compute_autocorrelations(data, max_lag):
    """
    Computes the autocorrelation matrix by normalizing the autocovariance matrices.

    Parameters:
        data (np.ndarray): Input data array with shape (n, 2).
        max_lag (int): Maximum lag for autocorrelation computation.

    Returns:
        np.ndarray: A 3D NumPy array with shape (max_lag+1, 2, 2),
                    where each slice is the autocorrelation matrix for a given lag.
    """
    autocov_matrices = compute_autocovariances(data, max_lag)

    # Extract variances (autocovariance at lag 0)
    variances = np.diag(autocov_matrices[0])  # Variances at lag 0
    stddev_matrix = np.outer(np.sqrt(variances), np.sqrt(variances))

    autocorr_matrices = []
    for lag in range(max_lag + 1):
        autocorr_matrix = autocov_matrices[lag] / stddev_matrix
        autocorr_matrices.append(autocorr_matrix)

    return np.array(autocorr_matrices)
    
    
    
    
    