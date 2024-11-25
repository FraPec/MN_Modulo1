from scipy.optimize import curve_fit
from scipy.stats import linregress 
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt


def numerical_derivative(data, locality=1, data_scale='linear'):
    # Check if locality is too large for the given dataset
    if locality > np.floor(data.shape[0] / 2) - 1:
        raise ValueError("Locality is too long compared with data shape")
    
    # Check if the data has the correct shape (N, 2)
    if data.shape[1] != 2:
        raise ValueError(f"Invalid data format. Required shape = (N, 2), given {data.shape}")
    
    # Check if the data scale is valid
    if data_scale not in ['linear', 'logxy', 'semilogx', 'semilogy']:
        raise ValueError("Invalid data scale. Valid inputs: 'linear', 'logxy', 'semilogx', 'semilogy'.")
    
    # Apply transformations based on the data scale
    if data_scale == 'logxy':
        if np.any(data <= 0):
            raise ValueError("Data contains non-positive values, cannot apply log10 in logxy scale")
        data = np.log10(data)  # Apply log10 to both x and y
    elif data_scale == 'semilogx':
        if np.any(data[:, 0] <= 0):
            raise ValueError("X contains non-positive values, cannot apply log10 in semilogx scale")
        data[:, 0] = np.log10(data[:, 0])  # Apply log10 to x only
    elif data_scale == 'semilogy':
        if np.any(data[:, 1] <= 0):
            raise ValueError("Y contains non-positive values, cannot apply log10 in semilogy scale")
        data[:, 1] = np.log10(data[:, 1])  # Apply log10 to y only
    
    
    # Calculate the number of valid points for derivative computation
    n_points = data.shape[0] - 2 * locality
    if n_points <= 0:
        raise ValueError("Locality too large for the given data size.")
    
    # Initialize an array to store the derivative results
    derivative_v = np.zeros((n_points, 2))
    
    # Compute the derivatives using linear regression
    for idx, i in enumerate(range(locality, data.shape[0] - locality)):
        # Select a window of points around the current index
        x_values = data[i - locality:i + locality + 1, 0]
        y_values = data[i - locality:i + locality + 1, 1]
        
        # Perform linear regression on the selected window
        fit_result = linregress(x_values, y_values)
        
        # Store the central x value and the computed slope (derivative)
        derivative_v[idx, 0] = data[i, 0]  # Central x value
        derivative_v[idx, 1] = fit_result.slope  # Slope as the derivative

    return derivative_v
        
      
           



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

def fit_function(x, a, b, m):
    return a * (1 - np.exp(-b * x**m)) 
    
if __name__ == "__main__":
    # Load and preprocess data
    data = load_binary_file("data_b0.54978_a0.01_L40.dat", 3)
    data = data[int(1e5):int(4e6), :]
    N = data.shape[0]

    # Generate block sizes
    block_sizes_v = np.unique(np.logspace(0, np.log10(1900000), 400, dtype=int))
    variance_v = np.zeros(block_sizes_v.shape)

    # Compute standard deviation for each block size
    for i, block_size in enumerate(block_sizes_v):
        variance_v[i] = blocking(data[:, 1], block_size)
        

    print(f"m_y = {np.mean(data[:, 1])}")
    print(variance_v)
    print(block_sizes_v)
    
    
    der_v = numerical_derivative(
        np.array([block_sizes_v, variance_v]).T,  # Convert to shape (N, 2)
        locality=5,
        data_scale = "logxy"
    )
        
    der_f = CubicSpline(der_v[:, 0], der_v[:, 1])    
    zeros_der = 10**der_f.roots()
    print(zeros_der)
                        

    # Fit parameters
    a = max(variance_v)
    b = (variance_v[3] / (a * block_sizes_v[3]**(1/2)))
    m = 1 
    p0 = [a, b, m]
    print(f"Starting parameters: a = {a}, b = {b}, m = {m}")
    max_block_size = zeros_der[0]
    mask = block_sizes_v < max_block_size
    popt, pcov = curve_fit(fit_function, block_sizes_v[mask], variance_v[mask], p0=p0, maxfev = 4000)
    a, b, m = popt
    residuals = (fit_function(block_sizes_v, a, b, m) - variance_v) / variance_v
    std_dev = np.sqrt(np.diag(pcov))
    print(f"A = {a} ± {std_dev[0]}, b = {b} ± {std_dev[1]}, m = {m} ± {std_dev[2]}")
    print(f"Covariance matrix:\n{pcov}")

    # Create subplots with shared x-axes
    fig, axs = plt.subplots(3, 1, figsize=(16, 9), sharex=True)  # Share x-axis

    # Plot data and fitted curve on the first subplot
    axs[0].scatter(block_sizes_v, variance_v, marker=".", label="data", zorder=0, color="red")
    axs[0].plot(block_sizes_v, fit_function(block_sizes_v, a, b, m), color="blue", label="fitted curve", zorder=1)
    axs[0].set_ylabel(r"$\sigma^2_{m_y} (k)$", fontsize=20)
    axs[0].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[0].legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    # Plot residuals on the second subplot
    axs[1].plot(block_sizes_v[mask], residuals[mask], label="residuals", color="green")
    axs[1].set_ylabel("Residuals", fontsize=20)
    axs[1].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[1].legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    axs[2].plot(10**der_v[:, 0], der_v[:, 1], label="numerical", marker=".", linestyle=" ", color="red", zorder=0)
    axs[2].plot(10**der_v[:, 0], der_f(der_v[:, 0]), label="spline interpolation", linestyle="-", color="blue", zorder=1)
    axs[2].set_xlabel("Block size, k", fontsize=20)
    axs[2].set_ylabel(r"$\frac{d \sigma^2_{m_y} (k)}{dk}$", fontsize=20)
    axs[2].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[2].legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    # Adjust layout and display the plots
    plt.tight_layout()
    
    # Create subplots with shared x-axes
    fig, axs = plt.subplots(3, 1, figsize=(16, 9), sharex=True)  # Share x-axis

    # Plot data and fitted curve on the first subplot
    axs[0].scatter(block_sizes_v, variance_v, marker=".", label="data", zorder=0, color="red")
    axs[0].plot(block_sizes_v, fit_function(block_sizes_v, a, b, m), color="blue", label="fitted curve", zorder=1)
    axs[0].set_ylabel(r"$\sigma^2_{m_y} (k)$", fontsize=20)
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[0].legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    # Plot residuals on the second subplot
    axs[1].plot(block_sizes_v[mask], residuals[mask], label="residuals", color="green")
    axs[1].set_ylabel("Residuals", fontsize=20)
    axs[1].set_xscale("log")
    axs[1].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[1].legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    axs[2].plot(10**der_v[:, 0], der_v[:, 1], label="numerical", marker=".", linestyle=" ", color="red", zorder=0)
    axs[2].plot(10**der_v[:, 0], der_f(der_v[:, 0]), label="spline interpolation", linestyle="-", color="blue", zorder=1)
    axs[2].set_xlabel("Block size, k", fontsize=20)
    axs[2].set_ylabel(r"$\frac{d \sigma^2_{m_y} (k)}{dk}$", fontsize=20)
    axs[2].set_xscale("log")
    axs[2].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[2].legend(fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    # Adjust layout and display the plots
    plt.tight_layout()
    plt.show()
    
    


