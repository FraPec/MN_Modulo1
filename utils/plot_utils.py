import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def truncate_at_first_negative(data):
    """
    Truncate data at the first occurrence of a negative value.

    Parameters:
        - data (list or np.ndarray): Input autocorrelation series.

    Returns:
        - np.ndarray: Truncated series up to the first negative value.
    """
    data = np.array(data)
    for idx, value in enumerate(data):
        if value < 0:
            return data[:idx]  # Return up to the first negative value
    return data  # Return full series if no negatives are found



def plot_autocorrelations(data_list, labels, max_lag, save_path, style="line", x_scale='linear', y_scale='linear', title=None):
    """
    Plot autocorrelations with customizable styles.

    Parameters:
        - data_list: List of autocorrelation series.
        - labels: List of labels for the series.
        - max_lag: Maximum lag.
        - save_path: Path to save the plot.
        - style: Plot style ('line', 'scatter', 'bar').
        - x_scale: Scale for the x-axis ('linear' or 'log').
        - y_scale: Scale for the y-axis ('linear' or 'log').
        - title: Title of the plot.
    """
    plt.figure(figsize=(10, 6))
    lags = np.arange(max_lag + 1)

    for i, data in enumerate(data_list):
        
        # Truncate data at the first negative value if y_scale is log
        if y_scale == 'log':
            data = truncate_at_first_negative(data)

        # Generate lags (length depends on truncated data)
        lags = np.arange(len(data))

        # Plot data based on style    
        if style == "line":
            plt.plot(lags, data, label=labels[i])
        elif style == "scatter":
            plt.scatter(lags, data, label=labels[i])
        elif style == "bar":
            plt.bar(lags, data, label=labels[i], alpha=0.5)




    plt.xlabel("Lag")
    plt.ylabel("Autocorrelation")
    plt.xscale(x_scale)
    plt.yscale(y_scale)
    if title:
        plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(save_path, dpi=300)
    plt.close
    
    
    
    

def generate_plots(autocorr_data, plot_dir, base_name, separate_plots):
    """
    Generate plots using the provided autocorrelation data.

    Parameters:
        autocorr_data (dict): Dictionary of autocorrelation arrays.
        plot_dir (str): Directory to save plots.
        base_name (str): Base name for output files.
        separate_plots (bool): Whether to generate separate plots.
    """
    # Generate matrix component plots
    plot_file_matrix = os.path.join(plot_dir, f"{base_name}_autocorr_matrix.png")
    plot_autocorrelations(
        [autocorr_data["mx-mx"], autocorr_data["mx-my"], autocorr_data["my-mx"], autocorr_data["my-my"]],
        ["mx-mx", "mx-my", "my-mx", "my-my"],
        max_lag=len(autocorr_data["mx-mx"]) - 1,
        save_path=plot_file_matrix
    )

    # Generate module_m and epsilon plots
    if separate_plots:
        plot_file_module = os.path.join(plot_dir, f"{base_name}_autocorr_module_m.png")
        plot_autocorrelations([autocorr_data["module_m"]], ["module_m"], max_lag=len(autocorr_data["module_m"]) - 1,
                              save_path=plot_file_module)

        plot_file_epsilon = os.path.join(plot_dir, f"{base_name}_autocorr_epsilon.png")
        plot_autocorrelations([autocorr_data["epsilon"]], ["epsilon"], max_lag=len(autocorr_data["epsilon"]) - 1,
                              save_path=plot_file_epsilon)
    else:
        plot_file_combined = os.path.join(plot_dir, f"{base_name}_autocorr_combined.png")
        plot_autocorrelations(
            [autocorr_data["module_m"], autocorr_data["epsilon"]],
            ["module_m", "epsilon"],
            max_lag=len(autocorr_data["module_m"]) - 1,
            save_path=plot_file_combined
        )  
    
 
 
 
 


def plot_blocking_variance(variances, save_path, title=None, x_label="Block Size", y_label="Variance"):
    """
    Plot the blocking variances in reverse order (from largest to smallest block size).

    Parameters:
        variances (dict): A dictionary where keys are block sizes and values are variances.
        save_path (str): Path to save the plot.
        title (str, optional): Title of the plot.
        x_label (str, optional): Label for the x-axis.
        y_label (str, optional): Label for the y-axis.
    """
    # Reverse the variances (largest block size first)
    block_sizes = np.array(list(variances.keys()))[::-1]
    variance_values = np.array(list(variances.values()))[::-1]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(block_sizes, variance_values, linestyle="", marker=".", markersize = 0.8)

    # Set logarithmic scales for x and y axes
    plt.xscale("log")
    plt.yscale("log")

    # Add labels, title, and legend
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if title:
        plt.title(title)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Save the plot
    plt.savefig(save_path, dpi=300)
    plt.close()

    print(f"[INFO] Blocking variance plot saved to {save_path}")   






def plot_jackknife_blocking_variance(variances, blocksizes, save_path, title=None, x_label="Block Size", y_label="Variance"):
    """
    Plot the variances obtained from Jackknife + blocking procedure against the blocksizes

    Parameters:
        variances (numpy.ndarray): A numpy array containing the variance of the variable we are analyzing 
        blocksizes (numpy.ndarray): A numpy array containing the corresponding blocksizes
        title (str, optional): Title of the plot.
        x_label (str, optional): Label for the x-axis.
        y_label (str, optional): Label for the y-axis.
    
    Returns:
        None
    """
    # Create the plot
    plt.figure(figsize=(10, 6)) 
    plt.plot(blocksizes, variances, linestyle="", marker=".", markersize = 0.8)

    # Set logarithmic scales for x and y axes
    plt.xscale("log")
    plt.yscale("log")

    # Add labels, title, and legend
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if title:
        plt.title(title)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Save the plot
    plt.savefig(save_path, dpi=300)
    plt.close()
    

def plot_fss_with_errors(x_values, y_values, errors, lattice_side_list=None, marker='o', cmap='tab10', xlabel="beta", ylabel=r"$\chi'$"):
    """ 
    Plots multiple datasets, one for each lattice_side, with error bars, distinct colors, and empty markers.
    
    Parameters:
        x_values (list of arrays): List of arrays where each array represents the x-values for a dataset.
        y_values (list of arrays): List of arrays where each array represents the y-values for a dataset.
        errors (list of arrays): List of arrays where each array contains the errors for the corresponding y-values.
        lattice_side_list (list of int, optional): List of lattice side lengths for each dataset.
        marker (str): Marker style, 'o' for circular markers by default.
        cmap (str): Name of the colormap to use for generating distinct colors.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
    
    Returns:
        None
    """
    num_datasets = len(y_values)
    colors = matplotlib.colormaps.get_cmap(cmap)(np.linspace(0, 1, num_datasets))  # Corrected line
    
    plt.figure(figsize=(10, 6))
    for i, (x, y, y_err) in enumerate(zip(x_values, y_values, errors)):
        if np.all(lattice_side_list):
            plt.errorbar(x, y, yerr=y_err, fmt=marker, ecolor=colors[i], linestyle='--', color=colors[i],
                         label=f'L {lattice_side_list[i]}')
        else:
            plt.errorbar(x, y, yerr=y_err, fmt=marker, ecolor=colors[i], linestyle='--', color=colors[i])
    
    plt.legend(fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel(xlabel, fontsize=20)
    plt.ylabel(ylabel, fontsize=20)
    plt.grid()
    plt.show()

