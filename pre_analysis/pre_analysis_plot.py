import os
import shutil
import numpy as np
import matplotlib.pyplot as plt


def plotting(x_v, y_v, xlabel, ylabel, xscale, yscale, plot_label, plot_title):
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.plot(x_v, y_v, "-", label=plot_label)
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.ylabel(ylabel, fontsize=20)
    plt.xlabel(xlabel, fontsize=20)
    plt.legend(fontsize=20)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.title(plot_title, fontsize=25)
    return


def calculate_up_to(lattice_side, factor, data_length):
    """
    Calcola il valore di 'up_to' basato su lattice_side, un fattore moltiplicativo e la lunghezza dei dati.
    
    Args:
        lattice_side (int): Dimensione del reticolo.
        factor (int): Fattore moltiplicativo per calcolare il massimo h.
        data_length (int): Lunghezza massima disponibile dei dati.
    
    Returns:
        int: Il valore corretto di 'up_to'.
    """
    calculated_up_to = factor * int(lattice_side**3)
    if calculated_up_to > data_length:
        print(f"Warning: up_to ({calculated_up_to}) modificato a {data_length} per compatibilità con i dati disponibili.")
    return min(calculated_up_to, data_length)


if __name__ == '__main__':
    import_path = "pre_analysis_data/pre_analysis_autocorr/"
    export_path = "pre_analysis_data/pre_analysis_autocorr_images/"

    # Controllo ed eliminazione della directory se esiste
    if os.path.exists(export_path):
        shutil.rmtree(export_path)
        print(f"Directory '{export_path}' eliminata.")
    
    # Ricreazione della directory
    os.makedirs(export_path, exist_ok=True)
    print(f"Directory '{export_path}' creata.")
    
    lattice_side_v = [10, 20, 30, 40, 50, 60, 70]
    beta_v = [0.3, 0.4, 0.5, 0.6]
    alpha_v = [0.001, 0.01, 0.1, 1]
    
    for lattice_side in lattice_side_v:
        lattice_export_path = os.path.join(export_path, f"lattice{lattice_side}")
        os.makedirs(lattice_export_path, exist_ok=True)
        
        for beta in beta_v:
            beta_export_path = os.path.join(lattice_export_path, f"beta{beta}")
            os.makedirs(beta_export_path, exist_ok=True)
            
            data_l = []
            labels_l = []

            for alpha in alpha_v:
                data_path = os.path.join(
                    import_path, f"L{lattice_side}_b{beta}_a{alpha}_autocorr.txt"
                )
                if not os.path.exists(data_path):
                    print(f"File {data_path} not found. Skipping.")
                    continue
                
                data_l.append(np.loadtxt(data_path, skiprows=1, delimiter=' '))
                labels_l.append(rf'$\alpha$ = {alpha:.3f}')
                
            if not data_l:
                print(f"No data found for lattice_side={lattice_side}, beta={beta}. Skipping.")
                continue
            
            x_lags = np.linspace(0, data_l[0].shape[0], data_l[0].shape[0])
            
            # Grafico normale
            plt.figure(figsize=(16, 9))
            for data, label in zip(data_l, labels_l):
                plotting(x_lags, data[:, 0], 'h', r'$C_{xx}(h)$', 'linear', 'linear',
                         plot_label=label, plot_title=rf"lattice = {lattice_side}, $\beta$ = {beta}")
            plt.savefig(os.path.join(beta_export_path, f"lattice{lattice_side}_b{beta}_autocorr_fig.pdf"))
            plt.close()
            
            # Grafico zoomato
            up_to = calculate_up_to(lattice_side, 6, data_l[0].shape[0])
            plt.figure(figsize=(16, 9))
            for data, label in zip(data_l, labels_l):
                plotting(x_lags[:up_to], data[:up_to, 0], 'h', r'$C_{xx}(h)$', 'linear', 'linear',
                         plot_label=label, plot_title=rf"lattice = {lattice_side}, $\beta$ = {beta}")
            plt.savefig(os.path.join(beta_export_path, f"zoomed_lattice{lattice_side}_b{beta}_autocorr_fig.pdf"))
            plt.close()
            
            # Grafico logaritmico zoomato
            up_to = calculate_up_to(lattice_side, 3, data_l[0].shape[0])
            plt.figure(figsize=(16, 9))
            for data, label in zip(data_l, labels_l):
                plotting(x_lags[:up_to], data[:up_to, 0], 'h', r'$C_{xx}(h)$', 'linear', 'log',
                         plot_label=label, plot_title=rf"lattice = {lattice_side}, $\beta$ = {beta}")
            plt.savefig(os.path.join(beta_export_path, f"zoomed_log_lattice{lattice_side}_b{beta}_autocorr_fig.pdf"))
            plt.close()