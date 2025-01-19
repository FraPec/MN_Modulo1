import sys
import os
import logging
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
from io_utils import setup_logging, load_config, prompt_user_choice, ensure_directory
from fss_utils import prepare_dataset_fss_plot
from interface_utils import navigate_directories

def update_config_file_paths(config):
    """Update the configuration paths based on user input."""
    file_name_means_input = input(f"Enter means file path (default: {config['paths']['file_name_means']}): ").strip()
    config['paths']['file_name_means'] = file_name_means_input or config['paths']['file_name_means']

    file_name_vars_input = input(f"Enter variances file path (default: {config['paths']['file_name_vars']}): ").strip()
    config['paths']['file_name_vars'] = file_name_vars_input or config['paths']['file_name_vars']

    fss_fit_results_input = input(f"Enter fit results file path (default: {config['paths']['file_name_fit_results']}): ").strip()
    config['paths']['file_name_fit_results'] = fss_fit_results_input or config['paths']['file_name_fit_results']

    # Prompt user for 'plot_dir' with a default value
    plot_dir_input = input(f"Enter plot directory path (default: {config['paths']['plot_dir']}): ").strip()
    config['paths']['plot_dir'] = plot_dir_input or config['paths']['plot_dir']
   
    return config

def chi_prime_f(beta, alpha, beta_pc, chi_prime_max):
    return alpha * (beta - beta_pc)**2 + chi_prime_max

def plot_fit_results(beta_fit, chi_prime_fit, dchi_prime_fit, popt, title=None, filename=None):
    beta_v = np.linspace(min(beta_fit), max(beta_fit), 100)
    plt.figure(figsize=(16, 9))
    plt.plot(beta_v, chi_prime_f(beta_v, *popt), label=r"Fit")
    plt.errorbar(beta_fit, chi_prime_fit, yerr=dchi_prime_fit, marker='.', linestyle='', label='Data')
    plt.grid()
    plt.xlabel(r"$\beta$", fontsize=20)
    plt.ylabel(r"$\chi$", fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    if title:
        plt.title(title, fontsize=20)
    plt.legend(fontsize=20)
    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=300)
    plt.show()

def fit_chi_prime(beta, chi_prime, dchi_prime, starting_params=None):
    popt, pcov = curve_fit(chi_prime_f, beta, chi_prime, p0=starting_params, sigma=dchi_prime, absolute_sigma=True)
    std_devs = np.sqrt(np.diag(pcov))
    res_sq = (chi_prime_f(beta, *popt) - chi_prime) ** 2
    chisq = np.sum(res_sq / dchi_prime ** 2)
    ndof = len(beta) - len(popt)
    return popt, pcov, std_devs, chisq, ndof

def create_starting_params(beta, chi):
    chi_max = np.max(chi)
    beta_c = beta[np.argmax(chi)]
    alpha = (chi[0] - chi_max) / (beta[0] - beta_c)**2
    return alpha, beta_c, chi_max

def print_and_confirm_config(config):
    print("Loaded configuration:")
    for key, value in config.items():
        print(f"{key}: {value}")
    return prompt_user_choice("Is the configuration correct?")

def get_new_beta_interval():
    beta_min = input("Enter new minimum beta value (press Enter to keep current minimum): ").strip()
    beta_max = input("Enter new maximum beta value (press Enter to keep current maximum): ").strip()
    return float(beta_min) if beta_min else None, float(beta_max) if beta_max else None

if __name__ == '__main__':
    setup_logging(log_dir="../logs/", log_file="fss_fit.log")
    
    try:
        config = load_config("../configs/fss.yaml")
        
        if not print_and_confirm_config(config):
            config = update_config_file_paths(config)

        df_means = pd.read_csv(config["paths"]["file_name_means"])
        df_vars = pd.read_csv(config["paths"]["file_name_vars"])
        beta_intervals = config["settings"]["beta_min_max"] 

        beta_list, means_data_set_list, std_devs_data_set_list, L_list = prepare_dataset_fss_plot(df_means, df_vars, "chi_prime")
        logging.info(f"Current L list:\n{L_list}")

        alpha_list = []
        beta_pc_list = []
        chi_prim_max_list = []
        dalpha_list = []
        dbeta_pc_list = []
        dchi_prim_max_list = []
        chi2_list = [] 
        ndof_list = []
        chi2_over_ndof = []

        for i in range(len(L_list)):
            logging.info(f"Current L: {L_list[i]}")
            
            original_beta = beta_list[i]
            original_means = means_data_set_list[i]
            original_std_devs = std_devs_data_set_list[i]
            

            while True:
                starting_params = create_starting_params(original_beta, original_means)
                logging.info(f"Starting parameters: {starting_params}")

                beta_min, beta_max = beta_intervals[i][0], beta_intervals[i][1]

                beta_mask = np.ones_like(original_beta, dtype=bool)
                if beta_min is not None:
                    beta_mask &= (original_beta >= beta_min)
                if beta_max is not None:
                    beta_mask &= (original_beta <= beta_max)

                beta_fit = original_beta[beta_mask]
                chi_prime_fit = original_means[beta_mask]
                dchi_prime_fit = original_std_devs[beta_mask]

                popt, pcov, std_devs, chisq, ndof = fit_chi_prime(beta_fit, chi_prime_fit, dchi_prime_fit, starting_params)
                std_devs = np.sqrt(np.diag(pcov))

                logging.info(f"Optimal parameters: alpha = {popt[0]} +- {std_devs[0]}, beta_pc = {popt[1]} +- {std_devs[1]}, chi_prime_max = {popt[2]} +- {std_devs[2]}")
                logging.info(f"Chi-squared/ndof: {chisq:.1f}/{ndof}")
                corr_mat = np.zeros(pcov.shape)
                for k in range(pcov.shape[0]):
                    for l in range(pcov.shape[0]):
                        corr_mat[k, l] = pcov[k, l] / (std_devs[k] * std_devs[l])
                logging.info(f"Correlation matrix:\n{corr_mat}")
                
                ensure_directory(config["paths"]["plot_dir"])
                filepath = os.path.join(config["paths"]["plot_dir"], f"chi_vs_beta_L{L_list[i]}.png")
                plot_fit_results(beta_fit, chi_prime_fit, dchi_prime_fit, popt, title=f"lattice side {L_list[i]}", filename=filepath)

                if prompt_user_choice("Do you want to fit again, changing beta interval?"):
                    beta_intervals[i] = get_new_beta_interval()
                else:
                    alpha_list.append(popt[0])
                    beta_pc_list.append(popt[1])
                    chi_prim_max_list.append(popt[2])
                    dalpha_list.append(std_devs[0])
                    dbeta_pc_list.append(std_devs[1])
                    dchi_prim_max_list.append(std_devs[2])
                    chi2_list.append(chisq) 
                    ndof_list.append(ndof)
                    chi2_over_ndof.append(chisq/ndof)
                    break
        
        # Save results to a DataFrame
        results_df = pd.DataFrame({
            'L': L_list,
            'beta_pc': beta_pc_list,
            'sigma_beta_pc': dbeta_pc_list,
            'max_chi_prime': chi_prim_max_list,
            'sigma_max_chi_prime': dchi_prim_max_list,
            'alpha': alpha_list,
            'sigma_alpha': dalpha_list,
            'chi2': chi2_list,
            'ndof': ndof_list,
            'chi2_over_ndof': chi2_over_ndof
        })
        
        # Save DataFrame to CSV
        results_df.to_csv(config['paths']['file_name_fit_results'], index=False)
    
    except Exception as main_e:
        logging.critical(f"Unexpected error in main script: {main_e}", exc_info=True)

