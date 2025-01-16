import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def list_folders(base_path):
    """
    List available folders in the given directory.
    """
    print("\nAvailable directories in:", base_path)
    for item in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, item)):
            print(f" - {item}")
            
            
def rescale_fss(beta, observable, L, beta_c, nu, exponent):
    """
    Rescale beta and observables for finite size scaling (FSS).
    """
    x_rescaled = (beta - beta_c) * L**(1 / nu)
    y_rescaled = observable * L**(-exponent)
    return x_rescaled, y_rescaled
    

# Select folder interactively
base_dir = os.getcwd()
while True:
    list_folders(base_dir)
    folder_name = input("\nEnter the name of the folder containing the data files (or '..' to go up): ").strip()
    if folder_name == "..":
        base_dir = os.path.dirname(base_dir)
    else:
        potential_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(potential_path):
            data_folder = potential_path
            break
        else:
            print("Invalid folder name. Please try again.")

print(f"\nData folder selected: {data_folder}")

# Dynamically construct file paths
filepaths = {
    5: os.path.join(data_folder, "fss_variables_lattice5.txt"),
    10: os.path.join(data_folder, "fss_variables_lattice10.txt"),
    15: os.path.join(data_folder, "fss_variables_lattice15.txt"),
    20: os.path.join(data_folder, "fss_variables_lattice20.txt"),
    25: os.path.join(data_folder, "fss_variables_lattice25.txt"),
}

# Critical parameters
beta_c = 0.454169  # Critical beta value
nu = 0.6717        # Critical exponent for FSS
gamma = 1.3178     # Susceptibility critical exponent

# Load the data
data = {}
for L, filepath in filepaths.items():
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}. Please check the path.")
        exit()
    df = pd.read_csv(filepath, delim_whitespace=True)
    data[L] = df

# 1. Plot physical quantities as a function of beta
quantities = {
    "abs_m_mean": r"$\langle |m| \rangle$",
    "E_mean": r"$\epsilon$",
    "C": r"$C$",
    "chi": r"$\chi$",
    "chi_prime": r"$\chi'$",
    "binder": r"$U$"
}

fig, axes = plt.subplots(3, 2, figsize=(12, 15))
axes = axes.ravel()

for i, (key, label) in enumerate(quantities.items()):
    ax = axes[i]
    for L, df in data.items():
        ax.plot(df["beta"], df[key], 'o-', label=f"L={L}", markersize=3)
    ax.set_title(label)
    ax.set_xlabel(r"$\beta$")
    ax.set_ylabel(label)
    ax.legend()

plt.tight_layout()
plt.show()

# 2. FSS plots (Rescaled quantities)
fss_quantities = {
    "abs_m_mean": (r"$\langle |m| \rangle $", 0),  # Example beta/nu
    "chi": (r"$\chi / L^{\gamma/\nu}$", gamma / nu),
    "chi_prime": (r"$\chi' / L^{\gamma/\nu}$", gamma / nu),
    "binder": (r"$U$", 0)  # Binder cumulant is dimensionless
}



fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.ravel()

for i, (key, (label, exponent)) in enumerate(fss_quantities.items()):
    ax = axes[i]
    for L, df in data.items():
        x_rescaled, y_rescaled = rescale_fss(df["beta"], df[key], L, beta_c, nu, exponent)
        ax.plot(x_rescaled, y_rescaled, 'o-', label=f"L={L}", markersize=3)
    ax.set_title(label)
    ax.set_xlabel(r"$(\beta - \beta_c)L^{1/\nu}$")
    ax.set_ylabel(label)
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.show()