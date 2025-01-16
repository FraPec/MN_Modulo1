import sys
import os
import numpy as np
import pandas as pd


# Add the utils directory to the system path to import custom utility functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from plot_utils import plot_fss_with_errors
from fss_utils import prepare_dataset_fss_plot



if __name__=='__main__':
    df_means = pd.read_csv("../secondary_quantities/secondary_quantities_means.csv")
    df_vars = pd.read_csv("../secondary_quantities/secondary_quantities_variances.csv")
    
    variable_name = "U"
    beta_U_list, U_means_data_set_list, vars_U_data_set_list, L_list = prepare_dataset_fss_plot(df_means, df_vars, variable_name)
    plot_fss_with_errors(beta_U_list, U_means_data_set_list, vars_U_data_set_list, lattice_side_list=L_list, marker='o', cmap='tab10', xlabel="beta", ylabel=r"U")
    
    variable_name = "chi_prime"
    beta_chi_prime_list, chi_prime_means_data_set_list, vars_chi_prime_data_set_list, L_list = prepare_dataset_fss_plot(df_means, df_vars, variable_name)
    plot_fss_with_errors(beta_chi_prime_list, chi_prime_means_data_set_list, vars_chi_prime_data_set_list, lattice_side_list=L_list, marker='o', cmap='tab10', xlabel="beta", ylabel=r"$\chi'$")

