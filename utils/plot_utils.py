import os
import numpy as np
import matplotlib.pyplot as plt


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
    

def plot_without_fits(data, results, beta_pc_fit_function, chi_max_fit_function, output_dir):
    """
    Function to plot scatterplots for beta_pc and chi_max without fit curves.
    The chi_max plot is in log-log scale.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Scatterplot for beta_pc(L)
    plt.figure(figsize=(6, 6))
    plt.errorbar(data['L'], data['beta_pc'], yerr=data['sigma_beta_pc'], fmt='o', label='Data', capsize=5)
    plt.xlabel("$L$")
    plt.ylabel("$\\beta_{pc}$")
    plt.title("Scatterplot of $\\beta_{pc}$ vs $L$")
    plt.grid()
    output_beta_pc_path = os.path.join(output_dir, "scatter_beta_pc.png")
    plt.savefig(output_beta_pc_path, dpi = 300)
    plt.close()
    print(f"[INFO] Scatterplot saved to {output_beta_pc_path}")
    
    # Scatterplot for chi_max(L) in log-log scale
    plt.figure(figsize=(6, 6))
    plt.scatter(data['L'], data['max_chi_prime'], marker='o', label='Data')
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("$L$")
    plt.ylabel("$\\chi_{\\text{max}}'$")
    plt.title("Scatterplot of $\\chi_{\\text{max}}'$ vs $L$")
    plt.grid(which="both", linestyle="--", linewidth=0.5)
    output_chi_max_path = os.path.join(output_dir, "scatter_chi_max_log_log.png")
    plt.savefig(output_chi_max_path, dpi = 300)
    plt.close()
    print(f"[INFO] Scatterplot saved to {output_chi_max_path}")

    
def plot_critical_exponents(data, output_dir):
    """
    Plots critical exponents (beta_c, 1/nu, gamma/nu, nu, gamma) vs L_min.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Plot beta_c vs L_min
    plt.figure(figsize=(8, 6))
    plt.errorbar(data['L_min'], data['beta_c'], yerr=data['beta_c_err'], fmt='o', label=r"$\beta_c$", capsize=5)
    plt.axhline(y=data['beta_c'].mean(), color='r', linestyle='-', label='Mean')
    plt.axhline(y=data['beta_c'].mean() + data['beta_c'].std(), color='r', linestyle='--', label='Mean $\pm$ Std')
    plt.axhline(y=data['beta_c'].mean() - data['beta_c'].std(), color='r', linestyle='--')
    plt.xlabel(r"$L_{\mathrm{min}}$")
    plt.ylabel(r"$\beta_c$")
    plt.title(r"$\beta_c$ vs $L_{\mathrm{min}}$")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'beta_c_vs_Lmin.png'))
    plt.close()

    # Plot 1/nu vs L_min
    plt.figure(figsize=(8, 6))
    plt.errorbar(data['L_min'], data['1_over_nu'], yerr=data['1_over_nu_err'], fmt='o', label=r"$1/\nu$", capsize=5)
    plt.axhline(y=data['1_over_nu'].mean(), color='r', linestyle='-', label='Mean')
    plt.axhline(y=data['1_over_nu'].mean() + data['1_over_nu'].std(), color='r', linestyle='--', label='Mean $\pm$ Std')
    plt.axhline(y=data['1_over_nu'].mean() - data['1_over_nu'].std(), color='r', linestyle='--')
    plt.xlabel(r"$L_{\mathrm{min}}$")
    plt.ylabel(r"$1/\nu$")
    plt.title(r"$1/\nu$ vs $L_{\mathrm{min}}$")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, '1_over_nu_vs_Lmin.png'))
    plt.close()

    # Plot gamma/nu vs L_min
    plt.figure(figsize=(8, 6))
    plt.errorbar(data['L_min'], data['gamma_over_nu'], yerr=data['gamma_over_nu_err'], fmt='o', label=r"$\gamma/\nu$", capsize=5)
    plt.axhline(y=data['gamma_over_nu'].mean(), color='r', linestyle='-', label='Mean')
    plt.axhline(y=data['gamma_over_nu'].mean() + data['gamma_over_nu'].std(), color='r', linestyle='--', label='Mean $\pm$ Std')
    plt.axhline(y=data['gamma_over_nu'].mean() - data['gamma_over_nu'].std(), color='r', linestyle='--')
    plt.xlabel(r"$L_{\mathrm{min}}$")
    plt.ylabel(r"$\gamma/\nu$")
    plt.title(r"$\gamma/\nu$ vs $L_{\mathrm{min}}$")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'gamma_over_nu_vs_Lmin.png'))
    plt.close()

    # Plot nu vs L_min
    plt.figure(figsize=(8, 6))
    plt.errorbar(data['L_min'], data['nu'], yerr=data['nu_err'], fmt='o', label=r"$\nu$", capsize=5)
    plt.axhline(y=data['nu'].mean(), color='r', linestyle='-', label='Mean')
    plt.axhline(y=data['nu'].mean() + data['nu'].std(), color='r', linestyle='--', label='Mean $\pm$ Std')
    plt.axhline(y=data['nu'].mean() - data['nu'].std(), color='r', linestyle='--')
    plt.xlabel(r"$L_{\mathrm{min}}$")
    plt.ylabel(r"$\nu$")
    plt.title(r"$\nu$ vs $L_{\mathrm{min}}$")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'nu_vs_Lmin.png'))
    plt.close()

    # Plot gamma vs L_min
    plt.figure(figsize=(8, 6))
    plt.errorbar(data['L_min'], data['gamma'], yerr=data['gamma_err'], fmt='o', label=r"$\gamma$", capsize=5)
    plt.axhline(y=data['gamma'].mean(), color='r', linestyle='-', label='Mean')
    plt.axhline(y=data['gamma'].mean() + data['gamma'].std(), color='r', linestyle='--', label='Mean $\pm$ Std')
    plt.axhline(y=data['gamma'].mean() - data['gamma'].std(), color='r', linestyle='--')
    plt.xlabel(r"$L_{\mathrm{min}}$")
    plt.ylabel(r"$\gamma$")
    plt.title(r"$\gamma$ vs $L_{\mathrm{min}}$")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'gamma_vs_Lmin.png'))
    plt.close()

    print(f"[INFO] All plots saved in {output_dir}")    
    
    
    
    
    
