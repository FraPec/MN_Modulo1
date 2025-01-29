# Simulation and Analysis of Critical Properties of Model XY in 3D.

In the following repository, the simulation and analysis of the O(2) model (also known as XY) are implemented in order to study its phase transition.

Short of `LICENSE`, the `.gitignore` and the current `README.md`, the structure of the repository is as follows:

- **simulations**: Includes all the C code (and some bash scripts) of the algorithm useful for generating the data (Markov Chains in binary files).
- **configs**: Contains the `.yaml` type configuration files used to set the parameters of the analyses done with Python.
- **mcmc_thermalization_analysis**: Contains Python code for thermalization analysis of simulation data.
- **data_processing**: Contains Python code useful for processing and cleaning the raw data (binary files) obtained from the simulations.
- **data_analysis**: Contains Python code to perform analysis of primary (blocking) and secondary (blocking+Jackknife) variables.
- **fss**: Includes Python code useful for the study of **Finite Size Scaling (FSS)**, to analyze the effects of finite size in the simulated systems and obtain the critical parameters of the O(2) model.
- **utils**: Encapsulates utilitarian functions and scripts that support various parts of the project, such as visualization tools or auxiliary functions.

