import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils/')))
# Import utility functions
from interface_utils import navigate_directories
from io_utils import load_csv, save_csv
from plot_utils import plot_without_fits, plot_critical_exponents



# === Helper Functions ===

def beta_pc_fit_function(L, beta_c, b, nu_inv):
    """Functional form for beta_pc(L) as in Eq. (5.5.4)."""
    return beta_c + b * L**(-nu_inv)

def chi_max_fit_function(L, c0, c1, gamma_over_nu):
    """Functional form for chi_max(L) as in Eq. (5.5.5)."""
    return c0 + c1 * L**(gamma_over_nu)


def perform_fits(data, L_min_values):
    """Perform fits for beta_pc and chi_max over different L_min values."""
    results = []
    for L_min in L_min_values:
        subset = data[data['L'] >= L_min]
        L = subset['L'].values
        beta_pc = subset['beta_pc'].values
        sigma_beta_pc = subset['sigma_beta_pc'].values
        chi_max = subset['max_chi_prime'].values
        sigma_chi_max = subset['sigma_max_chi_prime'].values
        
        # Fit beta_pc(L)
        popt_beta, pcov_beta = curve_fit(
            beta_pc_fit_function, L, beta_pc, sigma=sigma_beta_pc, absolute_sigma=True
        )
        beta_c, b, nu_inv = popt_beta
        beta_c_err, b_err, nu_inv_err = np.sqrt(np.diag(pcov_beta))
        
        chi_sq_beta_pc = np.sum((beta_pc - beta_pc_fit_function(L, *popt_beta))**2 / sigma_beta_pc**2)
        ndof_beta_pc = len(L) - len(popt_beta)
        
        # Fit chi_max(L)
        popt_chi, pcov_chi = curve_fit(
            chi_max_fit_function, L, chi_max, sigma=sigma_chi_max, absolute_sigma=True
        )
        c0, c1, gamma_over_nu = popt_chi
        c0_err, c1_err, gamma_over_nu_err = np.sqrt(np.diag(pcov_chi))
        
        chi_sq_chi_prime_max = np.sum((chi_max - chi_max_fit_function(L, *popt_chi))**2 / sigma_chi_max**2)
        ndof_chi_prime_max = len(L) - len(popt_chi)

        # Save results
        results.append({
            'L_min': L_min,
            'beta_c': beta_c, 'beta_c_err': beta_c_err,
            'b': b,
            'b_err': b_err, 
            'chi_sq_beta_pc': chi_sq_beta_pc,
            'ndof_beta_pc': ndof_beta_pc,
            '1_over_nu': nu_inv, '1_over_nu_err': nu_inv_err,
            'c0': c0, 'c0_err': c0_err,  # Aggiunto c0 e c0_err
            'c1': c1, 'c1_err': c1_err,  # Aggiunto c1 e c1_err
            'gamma_over_nu': gamma_over_nu, 'gamma_over_nu_err': gamma_over_nu_err,
            'chi_sq_chi_prime_max': chi_sq_chi_prime_max,
            'ndof_chi_prime_max': ndof_chi_prime_max
        })
    return pd.DataFrame(results)
    
    
    
def save_summary_statistics(data, output_dir):
    """
    Calculates and saves the mean and standard deviation of gamma and nu.
    
    Parameters:
        data (pd.DataFrame): Data containing gamma, nu, and their errors.
        output_dir (str): Directory where the summary CSV will be saved.
    
    Returns:
        None
    """
    # Calculate mean and standard deviation
    summary = {
        'Parameter': ['gamma_over_nu', '1_over_nu'],
        'Mean': [data['gamma_over_nu'].mean(), data['1_over_nu'].mean()],
        'Std_Dev': [data['gamma_over_nu'].std(), data['1_over_nu'].std()]
    }

    # Convert to DataFrame
    summary_df = pd.DataFrame(summary)
    
    # Save to CSV
    output_csv_path = os.path.join(output_dir, 'summary_statistics.csv')
    summary_df.to_csv(output_csv_path, index=False)
    print(f"[INFO] Summary statistics saved to {output_csv_path}")    
    

# === Main Execution ===
if __name__ == "__main__":
    # Seleziona il file di input
    # === Default Paths ===
    DEFAULT_INPUT_CSV = "../data/finite_size_scaling_data/"
    print("Select the input CSV file:")
    INPUT_CSV = navigate_directories(
        start_path=os.path.dirname(DEFAULT_INPUT_CSV),  # Usa la directory di default
        multi_select=False,
        file_extension=".csv"
    )[0]

    # Determina il file di output basandosi sul percorso del file di input
    OUTPUT_CSV = os.path.join(os.path.dirname(INPUT_CSV), "output_critical_values.csv")
    
    # Carica i dati dal file di input
    raw_data = load_csv(INPUT_CSV)
    
    # Esegui i fit per L_min
    L_min_range = [9, 12, 15]
    fit_results = perform_fits(raw_data, L_min_range)
    
    # Salva i risultati nel file di output
    save_csv(fit_results, OUTPUT_CSV)
    
    # Crea i grafici senza curve di fit
    plot_without_fits(raw_data, fit_results, beta_pc_fit_function, chi_max_fit_function, os.path.dirname(INPUT_CSV))
    
    # Crea i grafici critici usando l'output CSV
    critical_values_data = pd.read_csv(OUTPUT_CSV)
    plot_critical_exponents(critical_values_data, os.path.dirname(INPUT_CSV))
    
    # Salva le statistiche di gamma e nu
    save_summary_statistics(critical_values_data, os.path.dirname(INPUT_CSV))
    
    print(f"[INFO] Output saved to: {OUTPUT_CSV}")

    
