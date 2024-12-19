import os
import re
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script for the plot of various variables vs beta")
    parser.add_argument("--folder_path", type=str,required=True, 
            help="Folder that contains all the txt files to be plotted"
    )
    args = parser.parse_args()
    folder_path = args.folder_path

    dataframe_list = []
    L_list = []
    # Iterate over files in the folder
    for filename in os.listdir(folder_path):
        # Get the full path to the file
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file and has a .txt extension
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            match = re.search(r'\d+', filename)
            if match:
                L_list.append(int(match.group()))
                df_raw = pd.read_csv(file_path, sep='\s+', header=None, skiprows=1)
                df_raw.columns = ["variable_name", "mean", "variance", "beta"]
                df = df_raw.sort_values(by="beta")
                dataframe_list.append(df)
    
    E_means_list = []
    E_var_list = []
    abs_m_list = []
    abs_m_var_list = []
    m_squared_list = []
    m_squared_var_list = []
    m_fourth_list = []
    beta_list = []
    
    for df in dataframe_list:
        E_means_list.append(df[df.iloc[:, 0] == r"$E$"].iloc[:, 1])
        E_var_list.append(df[df.iloc[:, 0] == r"$E$"].iloc[:, 2])
        abs_m_list.append(df[df.iloc[:, 0] == r"$|\vec{m}|$"].iloc[:, 1])
        abs_m_var_list.append(df[df.iloc[:, 0] == r"$|\vec{m}|$"].iloc[:, 2]) 
        m_squared_list.append(df[df.iloc[:, 0] == r"$|\vec{m}|^2$"].iloc[:, 1]) 
        m_fourth_list.append(df[df.iloc[:, 0] == r"$|\vec{m}|^4$"].iloc[:, 1])
        beta_list.append(df[df.iloc[:, 0] == r"$|\vec{m}|^4$"].iloc[:, 3])
    
    # Transposed because we want to have (beta_number)x(lattice_number) array
    E_means_array = np.array(E_means_list).T
    E_var_array = np.array(E_var_list).T
    abs_m_array = np.array(abs_m_list).T
    abs_m_var_array = np.array(abs_m_var_list).T
    m_squared_array = np.array(m_squared_list).T
    m_fourth_array = np.array(m_fourth_list).T
    beta_array = np.array(beta_list).T
   
    # Plot energy means vs beta
    color_list = plt.cm.viridis(np.linspace(0, 1, len(L_list)))  # Dynamic color assignment
    for i, L in enumerate(L_list):
        plt.scatter(beta_array[:, i], E_means_array[:, i], label=f"L={L}", color=color_list[i])

    plt.xlabel("Beta")
    plt.ylabel("Energy Mean")
    plt.legend()
    plt.grid()
    plt.title("Energy Mean vs Beta for Different Lattice Sizes")
    plt.show()


    L_array = np.array(L_list)

    gamma = 1.3178
    nu = 0.67169
    beta_c = 0.4541652
    
    beta_scaled = np.zeros(beta_array.shape) #(beta_array - beta_c) * L_array ** (1/nu) 
    for i in range(abs_m_var_array.shape[1]):
        beta_scaled[:, i] = (beta_array[:, i] - beta_c) * L_array[i] ** (1/nu)
    chi_prime = np.zeros(abs_m_var_array.shape)
    for i in range(abs_m_var_array.shape[1]):
        chi_prime[:, i] = L_array[i] ** 3 * abs_m_var_array[:, i]
    print(chi_prime.shape, chi_prime)
    y_var = chi_prime / (L_array ** (gamma / nu))
    
    plt.figure()
    color_list = plt.cm.viridis(np.linspace(0, 1, len(L_list)))  # Dynamic color assignment
    for i, L in enumerate(L_list):
        plt.scatter(beta_scaled[:, i], y_var[:, i], label=f"L={L}", color=color_list[i])
    
    plt.legend()
    plt.grid()
    plt.show()
