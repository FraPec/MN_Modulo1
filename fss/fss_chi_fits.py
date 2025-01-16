import sys
import os
import logging
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Add the utils directory to the system path to import custom utility functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import setup_logging, load_config
from fss_utils import prepare_dataset_fss_plot


def chi_prime_f(beta, alpha, beta_pc, chi_prime_max):
    """
    Function to fit the max-zone of chi prime with a parable
    """
    return alpha * (beta - beta_pc)**2 + chi_prime_max

def fit_chi_prime(beta, chi_prime, dchi_prime, beta_interval=[0, 1e8], starting_params=None):
    """
    Function that performs the fit of chi_prime_f over the dataset provided
    """
    beta_fit = beta[(beta>beta_interval[0]) & (beta<beta_interval[1])]
    chi_prime_fit = chi_prime[(beta>beta_interval[0]) & (beta<beta_interval[1])]
    dchi_prime_fit = dchi_prime[(beta>beta_interval[0]) & (beta<beta_interval[1])]

    popt, pcov = curve_fit(chi_prime_f, beta_fit, chi_prime_fit, p0=starting_params, sigma=dchi_prime_fit, absolute_sigma=True)
    std_devs = np.sqrt(np.diag(pcov))
    res_sq = (chi_prime_f(beta_fit, *popt) - chi_prime_fit)**2
    chisq = np.sum(res_sq / dchi_prime_fit**2)
    
    beta_v = np.linspace(min(beta_fit), max(beta_fit), 100)
    plt.plot(beta_v, chi_prime_f(beta_v, *popt))
    plt.scatter(beta_fit, chi_prime_fit)
    plt.show()
    print(chisq)
    return 

if __name__ == '__main__':

    # Setup logging
    log_dir = "../logs/"
    log_file = "fss_fit.log"
    setup_logging(log_dir=log_dir, log_file=log_file)
    
    try:
        # Load and verify the configuration
        config_path = "../configs/fss.yaml"
        config = load_config(config_path)
        logging.info("Loaded configuration:")
        for key, value in config.items():
            logging.info(f"{key}: {value}\n")

        df_means = pd.read_csv(config["paths"]["file_name_means"])
        df_vars = pd.read_csv(config["paths"]["file_name_vars"])
        
        i = -1
        beta_list, means_data_set_list, std_devs_data_set_list, L_list = prepare_dataset_fss_plot(df_means, df_vars, "chi_prime")
        logging.info(f"Current L {L_list[i]}")
        starting_params = [-2e6, 0.4525, 38]
        fit_chi_prime(beta_list[i], means_data_set_list[i], std_devs_data_set_list[i], beta_interval=[0.449, 0.456], starting_params=starting_params)
    except Exception as main_e:
        # Log any unexpected errors
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)


