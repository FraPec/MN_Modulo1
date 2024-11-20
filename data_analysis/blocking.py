from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt




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
    sigma_squared = 1 / ((N/block_size) * (N/block_size - 1)) * np.sum(np.power(data_res_k, 2))
    return sigma_squared

def fit_function(x, a, b, m):
    return a * (1 - np.exp(-b * x**m)) 

if __name__ == "__main__":
    # Load and preprocess data
    data = load_binary_file("data_b0.35404_a0.01_L30.dat", 3)
    data = data[int(1e5):int(4e6), :]
    N = data.shape[0]

    # Generate block sizes
    block_sizes_v = np.unique(np.logspace(0, np.log10(400000), 400, dtype=int))
    sigma_v = np.zeros(block_sizes_v.shape)

    # Compute standard deviation for each block size
    for i, block_size in enumerate(block_sizes_v):
        sigma_v[i] = np.sqrt(blocking(data[:, 1], block_size))

    print(f"m_x = {np.mean(data[:, 1])}")
    print(sigma_v)
    print(block_sizes_v)

    # Fit parameters
    a = 5e-4
    b = (sigma_v[3] / (5e-4 * block_sizes_v[3]**(1/2)))
    m = 1 / 2
    p0 = [a, b, m]
    popt, pcov = curve_fit(fit_function, block_sizes_v, sigma_v, p0=p0)
    a, b, m = popt
    std_dev = np.sqrt(np.diag(pcov))
    print(f"A = {a} ± {std_dev[0]}, b = {b} ± {std_dev[1]}, m = {m} ± {std_dev[2]}")
    print(f"Covariance matrix:\n{pcov}")

    # Create subplots with shared x-axes
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)  # Share x-axis

    # Plot data and fitted curve on the first subplot
    axs[0].scatter(block_sizes_v, sigma_v, marker=".", label="data")
    axs[0].plot(block_sizes_v, fit_function(block_sizes_v, a, b, m), color="red", label="fitted curve")
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_ylabel(r"$\sigma_{m_x}$", fontsize=14)
    axs[0].set_title("Fitted Curve vs Data", fontsize=16)
    axs[0].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[0].legend(fontsize=12)

    # Plot residuals on the second subplot
    residuals = fit_function(block_sizes_v, a, b, m) - sigma_v
    axs[1].plot(block_sizes_v, residuals, label="residuals", color="red")
    axs[1].set_xscale("log")
    axs[1].set_xlabel("Block size", fontsize=14)
    axs[1].set_ylabel("Residuals", fontsize=14)
    axs[1].set_title("Residuals Plot", fontsize=16)
    axs[1].grid(True, which="both", linestyle="--", linewidth=0.5)
    axs[1].legend(fontsize=12)

    # Adjust layout and display the plots
    plt.tight_layout()
    plt.show()


