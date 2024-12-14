import os
import re
import argparse
import numpy as np
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script for computing all the quantities useful for finite size scaling")
    parser.add_argument("--folder_path", type=str, required=True, 
                        help="Folder that contains all the txt files we want to analyze")
    parser.add_argument("--output_name", type=str, default="lattice.txt",
            help="Name of the output files, one for each lattice size")
    args = parser.parse_args()
    folder_path = args.folder_path
    output_name = args.output_name

    # Initialize lists to store results
    dim = 3  # dimensionality
    L_list = []
    mx_means_list, mx_var_list = [], []
    my_means_list, my_var_list = [], []
    E_means_list, E_var_list = [], []
    abs_m_list, abs_m_var_list = [], []
    m_squared_list, m_fourth_list = [], []

    # Single loop for file reading and data extraction
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Match lattice size (L) from the filename
        match = re.search(r'lattice(\d+)', filename)
        if match:
            L_list.append(int(match.group(1)))  # Extract L value

        # Process only .txt files
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            # Read and sort the DataFrame
            df = pd.read_csv(file_path, sep=r'\s+', header=None, skiprows=1,
                             names=["variable_name", "mean", "variance", "beta"])
            df = df.sort_values(by="beta")

            # Extract required data in a single pass
            mx_means_list.append(df.loc[df["variable_name"] == r"$m_x$", "mean"].values)
            mx_var_list.append(df.loc[df["variable_name"] == r"$m_x$", "variance"].values)
            my_means_list.append(df.loc[df["variable_name"] == r"$m_y$", "mean"].values)
            my_var_list.append(df.loc[df["variable_name"] == r"$m_y$", "variance"].values)
            E_means_list.append(df.loc[df["variable_name"] == r"$E$", "mean"].values)
            E_var_list.append(df.loc[df["variable_name"] == r"$E$", "variance"].values)
            abs_m_list.append(df.loc[df["variable_name"] == r"$|\vec{m}|$", "mean"].values)
            abs_m_var_list.append(df.loc[df["variable_name"] == r"$|\vec{m}|$", "variance"].values)
            m_squared_list.append(df.loc[df["variable_name"] == r"$|\vec{m}|^2$", "mean"].values)
            m_fourth_list.append(df.loc[df["variable_name"] == r"$|\vec{m}|^4$", "mean"].values)
    
    # Convert lists to arrays and sort by lattice size
    sorted_indices = np.argsort(np.array(L_list))
    L_list = np.array(L_list)[sorted_indices]
    mx_means_array = np.array(mx_means_list)[sorted_indices].T
    my_means_array = np.array(my_means_list)[sorted_indices].T
    abs_m_array = np.array(abs_m_list)[sorted_indices].T
    E_means_array = np.array(E_means_list)[sorted_indices].T
    m_squared_array = np.array(m_squared_list)[sorted_indices].T
    m_fourth_array = np.array(m_fourth_list)[sorted_indices].T
    beta_array = np.unique(df.loc[:, "beta"].values).T
    print(beta_array)

    # Compute derived quantities
    C = (L_list**dim) * np.array(E_var_list)[sorted_indices].T
    chi = (L_list**dim) * m_squared_array
    chi_prime = (L_list**dim) * np.array(abs_m_var_list)[sorted_indices].T
    binder = m_fourth_array / (m_squared_array**2)

    # Convert lists to arrays and sort by lattice size
    sorted_indices = np.argsort(L_list)
    L_list = np.array(L_list)[sorted_indices]
    mx_means_array = np.array(mx_means_list)[sorted_indices].T
    my_means_array = np.array(my_means_list)[sorted_indices].T
    abs_m_array = np.array(abs_m_list)[sorted_indices].T
    E_means_array = np.array(E_means_list)[sorted_indices].T
    m_squared_array = np.array(m_squared_list)[sorted_indices].T
    m_fourth_array = np.array(m_fourth_list)[sorted_indices].T

    # Compute derived quantities
    C = (L_list**dim) * np.array(E_var_list)[sorted_indices].T
    chi = (L_list**dim) * m_squared_array
    chi_prime = (L_list**dim) * np.array(abs_m_var_list)[sorted_indices].T
    binder = m_fourth_array / (m_squared_array**2)

    # Example variables (replace with actual data)
    variables_d = {
        "beta_array": beta_array,
        "mx_means_array": mx_means_array,
        "my_means_array": my_means_array,
        "abs_m_array": abs_m_array,
        "E_means_array": E_means_array,
        "m_squared_array": m_squared_array,
        "m_fourth_array": m_fourth_array,
        "C": C,
        "chi": chi,
        "chi_prime": chi_prime,
        "binder": binder
    }

    for i_lattice, L in enumerate(L_list):
        array_to_save = np.zeros((beta_array.shape[0], len(variables_d)))
        array_to_save[:, 0] = beta_array
        array_to_save[:, 1] = mx_means_array[:, i_lattice]
        array_to_save[:, 2] = my_means_array[:, i_lattice]
        array_to_save[:, 3] = abs_m_array[:, i_lattice]
        array_to_save[:, 4] = E_means_array[:, i_lattice]
        array_to_save[:, 5] = m_squared_array[:, i_lattice]
        array_to_save[:, 6] = m_fourth_array[:, i_lattice]
        array_to_save[:, 7] = C[:, i_lattice]
        array_to_save[:, 8] = chi[:, i_lattice]
        array_to_save[:, 9] = chi_prime[:, i_lattice]
        array_to_save[:, 10] = binder[:, i_lattice]
        basename, ext = os.path.splitext(output_name)
        filename = basename + str(L) + ext
        np.savetxt(filename, array_to_save, header="beta mx_mean my_mean abs_m_mean E_mean m_squared_mean m_fourth_mean C chi chi_prime binder", comments='') 


