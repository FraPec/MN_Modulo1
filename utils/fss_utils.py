import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def prepare_dataset_fss_plot(df_means, df_vars, variable_name):
    """
    Prepares datasets from two DataFrames for plotting with plot_fss_with_errors.
    
    This function sorts the input DataFrames by 'beta', extracts the means and variances 
    for the specified variable, and groups the data by lattice side length.
    
    Parameters:
        df_means (pd.DataFrame): DataFrame containing mean values for different variables.
        df_vars (pd.DataFrame): DataFrame containing variance values for different variables.
        variable_name (str): The name of the variable to extract means and variances for.
        
    Returns:
        tuple: Four lists containing beta values, mean datasets, variance datasets, 
               and lattice side lengths.
    """
    df_means_sorted_b = df_means.sort_values(by='beta')
    df_vars_sorted_b = df_vars.sort_values(by='beta')
    means_data_set_list = []
    std_devs_data_set_list = []
    beta_list = []
    L_list = np.unique(df_vars_sorted_b["L"].values)
    for L in L_list:
        std_devs_data_set_list.append(np.sqrt(df_vars_sorted_b[df_vars_sorted_b["L"]==L][f"var_{variable_name}"].values))
        means_data_set_list.append(df_means_sorted_b[df_means_sorted_b["L"]==L][f"{variable_name}_mean"].values)
        beta_list.append(df_means_sorted_b[df_means_sorted_b["L"]==L]["beta"].values)
    
    return beta_list, means_data_set_list, std_devs_data_set_list, L_list


def chi_prime_f(beta, alpha, beta_pc, chi_prime_max):
    """
    Functional form of chi prime for fitting purposes.
    
    Args:
        beta (float or np.ndarray): The independent variable, beta.
        alpha (float): Parameter controlling the curvature.
        beta_pc (float): Critical beta value.
        chi_prime_max (float): Maximum value of chi prime.
        
    Returns:
        float or np.ndarray: Calculated chi prime values.
    """
    return alpha * (beta - beta_pc)**2 + chi_prime_max


def fit_chi_prime(beta, chi_prime, dchi_prime, starting_params=None):
    """
    Fits the chi prime data using curve fitting.
    
    Args:
        beta (np.ndarray): Beta values.
        chi_prime (np.ndarray): Chi prime values.
        dchi_prime (np.ndarray): Standard deviations of chi prime.
        starting_params (list, optional): Initial parameters for the fit.
        
    Returns:
        tuple: Optimal parameters, covariance matrix, standard deviations,
               chi-squared value, and degrees of freedom.
    """
    popt, pcov = curve_fit(chi_prime_f, beta, chi_prime, p0=starting_params, sigma=dchi_prime, absolute_sigma=True)
    std_devs = np.sqrt(np.diag(pcov))
    res_sq = (chi_prime_f(beta, *popt) - chi_prime) ** 2
    chisq = np.sum(res_sq / dchi_prime ** 2)
    ndof = len(beta) - len(popt)
    return popt, pcov, std_devs, chisq, ndof


def create_starting_params(beta, chi):
    """
    Creates starting parameters for fitting based on initial data.
    
    Args:
        beta (np.ndarray): Beta values.
        chi (np.ndarray): Chi values.
        
    Returns:
        tuple: Initial parameters alpha, beta_c, and chi_max.
    """
    chi_max = np.max(chi)
    beta_c = beta[np.argmax(chi)]
    alpha = (chi[0] - chi_max) / (beta[0] - beta_c)**2
    return alpha, beta_c, chi_max


def get_new_beta_interval():
    """
    Prompts the user to enter a new beta interval.
    
    Returns:
        tuple: New minimum and maximum beta values.
    """
    beta_min = input("Enter new minimum beta value (press Enter to keep current minimum): ").strip()
    beta_max = input("Enter new maximum beta value (press Enter to keep current maximum): ").strip()
    return float(beta_min) if beta_min else None, float(beta_max) if beta_max else None
