from scipy.optimize import curve_fit
from scipy.stats import linregress 
from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt
import argparse

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

def fit_function(x, a, b, m):
    return a * (1 - np.exp(-b * x**m)) 
  
def plot_blocking_results(block_sizes_v, variance_v, der_v, der_f, residuals, mask, popt, plot_name, datafile_name, variable_name, std_dev):
    # Create subplots with shared x-axes
    fig, axs = plt.subplots(3, 1, figsize=(16, 9), sharex=True)  # Share x-axis
    for ax in axs:
        ax.tick_params(axis='both', which='major', labelsize=15)
        ax.tick_params(axis='both', which='minor', labelsize=15) 

    title = variable_name + ", " + datafile_name 
    plt.suptitle(title, fontsize=25)

    # Plot data and fitted curve on the first subplot
    axs[0].scatter(block_sizes_v, variance_v, marker=".", label="data", zorder=0, color="red")
    axs[0].plot(block_sizes_v, fit_function(block_sizes_v, a, b, m), color="blue", label="fitted curve", zorder=1)
    axs[0].set_ylabel(rf"Var({variable_name}) (k)", fontsize=20)
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[0].legend(fontsize=16)

    # Plot residuals on the second subplot
    axs[1].plot(block_sizes_v[mask], residuals[mask], label="residuals", color="green")
    axs[1].set_ylabel("Residuals", fontsize=20)
    axs[1].set_xscale("log")
    axs[1].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[1].legend(fontsize=16)

    axs[2].plot(10**der_v[:, 0], der_v[:, 1], label="numerical", marker=".", linestyle=" ", color="red", zorder=0)
    axs[2].plot(10**der_v[:, 0], der_f(der_v[:, 0]), label="spline interpolation", linestyle="-", color="blue", zorder=1)
    axs[2].set_xlabel("Block size, k", fontsize=20)
    axs[2].set_ylabel(rf"dVar({variable_name})/dk", fontsize=20)
    axs[2].set_xscale("log")
    axs[2].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[2].legend(fontsize=16)

    # Adjust layout and display the plots
    plt.tight_layout()
    plt.savefig(plot_name)
    
    


if __name__ == "__main__":
    # Section to deal with command lines from terminal
    parser = argparse.ArgumentParser(description="Fit and plot to estimate the std dev for the sample means")
    parser.add_argument("--input_datafile", type=str,required=True, 
            help="Name of the input data file to analize with blocking")
    parser.add_argument("--plot_name", type=str, required=True, 
            help="Name of the plotted figures of the blocking analysis. To such name will be added the _var for each of the plotted variables)")
    parser.add_argument("--locality", type=int, default=5, 
            help="Integer to choose how many nearest neighbor to involve in the derivative computation")
    args = parser.parse_args()
    filename = args.input_datafile
    plot_name = args.plot_name

    # Load and preprocess data
    data = np.loadtxt(filename)
    N = data.shape[0]

    # Generate a list of all the variables to compute
    var_names = [r"blocksize", r"$m_x$", r"$m_y$", r"$E$", r"$|\vec{m}|$", r"$|\vec{m}|^2$",  r"$|\vec{m}|^4$"]
    var_arrays = [data[:, i] for i in range(data.shape[1])]

    for var_index, (var_name, var_array) in enumerate(zip(var_names, var_arrays)):
        # Find numerical derivative
        der_v = numerical_derivative(
                np.array([block_sizes_v, variances_from_blocking[:, var_index]]).T,  # Convert to shape (N, 2)
            locality=args.locality,
            data_scale = "logxy"
        )

        # Create spline of such derivative
        der_f = CubicSpline(der_v[:, 0], der_v[:, 1])    
        # Find zeros of such derivative
        zeros_der = 10**der_f.roots()
        # Take such zero as max_block_size to use for fit                
        max_block_size = zeros_der[0]

        # Fit
        # Initial guess for parameters
        a = max(variances_from_blocking[:, var_index])
        b = (variances_from_blocking[3, var_index] / (a * block_sizes_v[3]**(1/2)))
        m = 1 
        p0 = [a, b, m]
        print(f"Starting parameters: a = {a}, b = {b}, m = {m}")
        # Use the max_block_size found with 0 of the derivative
        mask = block_sizes_v < max_block_size
        # Fitting procedure
        popt, pcov = curve_fit(fit_function, block_sizes_v[mask], variances_from_blocking[:, var_index][mask], p0=p0, maxfev = 4000)
        a, b, m = popt
        # Compute residuals and plot parameters with their std devs
        residuals = (fit_function(block_sizes_v, a, b, m) - variances_from_blocking[:, var_index]) / variances_from_blocking[:, var_index]
        std_devs_fit = np.sqrt(np.diag(pcov))
        print(f"A = {a} ± {std_devs_fit[0]}, b = {b} ± {std_devs_fit[1]}, m = {m} ± {std_devs_fit[2]}")
        print(f"Covariance matrix:\n{pcov}")

        # Take the sqrt of a as an estimation of the plateau
        var_stds.append(np.sqrt(a))

        # Managing the plot name

        plot_blocking_results(block_sizes_v, variances_from_blocking[:, var_index], der_v, der_f, residuals, mask, popt, plot_name, filename, variable_name, std_dev)  
    
