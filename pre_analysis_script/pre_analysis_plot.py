import multivar_autocorr.py

def plotting(x_v, y_v, xlabel, ylabel, xscale, yscale, name):
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.plot(x_v, y_v, ".-")
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.grid()
    plt.ylabel(ylabel, fontsize = 20)
    plt.xlabel(xlabel, fontsize = 20)
    return


if __name__ == '__main__':
   
    personal_path = "/home/francesco/Documents/coding_projects/"
    repo_path = "MN_Modulo1/pre_analysis_data/autocorr/"
    path = os.path.join(personal_path, repo_path)
    autocorr_path = os.path.join(personal_path, repo_path, "pre_analysis_autocorr")
