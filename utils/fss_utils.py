import numpy as np
import pandas as pd


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
