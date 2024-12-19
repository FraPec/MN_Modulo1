import os
import shutil
import argparse
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Section to deal with command lines from terminal
    parser = argparse.ArgumentParser(description="Program to plot autocorrelation for a set of files in a folder")
    parser.add_argument("--import_path", type=str, required=True,
            help="Folder in which all the autocorrelation files are stored")
    parser.add_argument("--plot_folder", type=str, default="plot_folder/",
            help="Folder in which all the plots will be stored")
    args = parser.parse_args()
    import_path = args.import_path
    export_path = args.plot_folder

    # Controllo ed eliminazione della directory se esiste
    if os.path.exists(export_path):
        shutil.rmtree(export_path)
        print(f"Directory '{export_path}' eliminata.")
    
    # Ricreazione della directory
    os.makedirs(export_path, exist_ok=True)
    print(f"Directory '{export_path}' creata.")
    
    for file_name in os.listdir(import_path):
        file_path = os.path.join(import_path, file_name)
        # Check if it has a .dat or .bin extension
        if file_name.endswith(('.txt')):
            base_name, ext = os.path.splitext(file_name) # split filename from its extension
            output_file = os.path.join(
                    export_path, base_name + '.png'
            )
            data_array = np.loadtxt(file_path, skiprows=1)
            x_lags = np.linspace(1, data_array.shape[0], num=data_array.shape[0])
            # Grafico normale
            plt.figure(figsize=(16, 9))
            plt.title(f"File: {base_name}", fontsize=20)
            if "magn" in base_name:
                plt.plot(x_lags, data_array[:, 0], label=r"Autocorr($m_x m_y$)")
                plt.plot(x_lags, data_array[:, 1], label=r"Corr($m_x m_y$)")
                plt.plot(x_lags, data_array[:, 2], label=r"Corr($m_y m_x$)")
                plt.plot(x_lags, data_array[:, 3], label=r"Autocorr($m_y m_y$)")
            if "sq_mod" in base_name:
                plt.plot(x_lags, data_array, label=r"Autocorr($|\vec{m}|^2$)")
            if "energy" in base_name:
                plt.plot(x_lags, data_array, label=r"Autocorr($E_{per \ site}$)")
            plt.legend(fontsize=20)
            plt.xlabel("h", fontsize=20)
            plt.xscale("log")
            plt.xticks(fontsize=15)
            plt.yticks(fontsize=15)
            plt.grid()
            plt.savefig(output_file, dpi=300)
            plt.close()

