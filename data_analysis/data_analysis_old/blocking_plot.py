import argparse
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress 
from scipy.interpolate import CubicSpline

# Function to extract the value near 'b' in the filename
def extract_beta_value(filename):
    # Regular expression to match the pattern 'b' followed by a number (including decimal point)
    match = re.search(r'b([0-9\.]+)', filename)
    if match:
        # Return the value found after 'b'
        return float(match.group(1))
    else:
        return None  # Return None if no match is found

def fit_function(x, a, b):
    return a * (1 - np.exp(-b * x)) 
  
def plot_blocking_results(block_sizes_v, variance_v, residuals, mask, popt, plot_name, datafile_name, variable_name):
    # Create subplots with shared x-axes
    fig, axs = plt.subplots(2, 1, figsize=(16, 9), sharex=True)  # Share x-axis
    for ax in axs:
        ax.tick_params(axis='both', which='major', labelsize=15)
        ax.tick_params(axis='both', which='minor', labelsize=15) 

    title = variable_name + ", " + datafile_name 
    plt.suptitle(title, fontsize=25)

    # Plot data and fitted curve on the first subplot
    axs[0].scatter(block_sizes_v, variance_v, marker=".", label="data", zorder=0, color="red")
    axs[0].plot(block_sizes_v, fit_function(block_sizes_v, a, b), color="blue", label="fitted curve", zorder=1)
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
    parser.add_argument("--max_block_size", type=int, required=True, 
            help="Integer to choose what's the max block size to use for the fit")
    parser.add_argument("--txt_file", type=str, required=True,
            help="txt file in which variances estimated with fitting procedure are going to be written")

    args = parser.parse_args()
    filename = args.input_datafile
    plot_name = args.plot_name
    max_block_size = args.max_block_size

    # Load and preprocess data
    blocking_data = np.loadtxt(filename, skiprows=2)
    means = blocking_data[0, 1:]
    block_sizes_v = blocking_data[1:, 0]
    variances_from_blocking = blocking_data[1:, 1:]
    N = variances_from_blocking.shape[0]

    # Generate a list of all the variables to compute
    var_names = [r"$m_x$", r"$m_y$", r"$E$", r"$|\vec{m}|$", r"$|\vec{m}|^2$",  r"$|\vec{m}|^4$"]
    var_arrays = [variances_from_blocking[:, i] for i in range(variances_from_blocking.shape[1])]
    variances = []
   
    if not os.path.exists(args.txt_file):
        write_title_string = True
    else:
        write_title_string = False
    
    with open(args.txt_file, "a") as file:
        if write_title_string:
            file.write(f"# variable_name, mean, variance, beta\n")

        for var_index, (var_name, var_array) in enumerate(zip(var_names, var_arrays)):

            # Fit
            # Initial guess for parameters
            a = max(variances_from_blocking[:, var_index])
            b = (variances_from_blocking[0, var_index] / (a * block_sizes_v[0]))
            p0 = [a, b]
            print(f"Starting parameters: a = {a}, b = {b}")
            # Use the max_block_size found with 0 of the derivative
            mask = block_sizes_v < max_block_size
            # Fitting procedure
            popt, pcov = curve_fit(fit_function, block_sizes_v[mask], variances_from_blocking[mask, var_index], p0=p0, maxfev = 4000)
            a, b = popt
            # Compute residuals and plot parameters with their std devs
            residuals = (fit_function(block_sizes_v, a, b) - variances_from_blocking[:, var_index]) / variances_from_blocking[:, var_index]
            std_devs_fit = np.sqrt(np.diag(pcov))
            print(f"A = {a} ± {std_devs_fit[0]}, b = {b} ± {std_devs_fit[1]}")
            print(f"Covariance matrix:\n{pcov}")

            # Take the sqrt of a as an estimation of the plateau
            variances.append(a)
            base_name, extension = os.path.splitext(plot_name)
            plot_name_current_var = base_name + var_name + ".png"
            # Managing the plot name
            plot_blocking_results(block_sizes_v, variances_from_blocking[:, var_index], residuals, mask, popt, plot_name_current_var, filename, var_name) 
            
            beta = extract_beta_value(filename)
            file.write(f"{var_name} {means[var_index]} {a} {beta}\n")

