#!/bin/bash

data_set="5_25_"

# Base input and output paths for blocking
input_blocking="data${data_set}/lattice"
output_blocking_prefix="blocked_data${data_set}/lattice"
log_blocking_prefix="blocking_lattice${data_set}"

# Base paths for blocking plot
input_plot_prefix="blocked_data${data_set}/lattice"
output_plot_prefix="plots${data_set}/lattice"
sigma_output_prefix="sigma_outputs${data_set}/lattice"
log_blocking_plot_prefix="blocking_plot_lattice${data_set}"

# Loop through the desired suffixes
for suffix in 5 10 15 20 25; do
    # Run the blocking script
    ./blocking.sh "${input_blocking}${suffix}" "${output_blocking_prefix}${suffix}" > "${log_blocking_prefix}${suffix}.out"

    # Run the blocking plot script
    ./blocking_plot.sh "${input_plot_prefix}${suffix}" "${output_plot_prefix}${suffix}" "${sigma_output_prefix}${suffix}.txt" 1000 8 > "${log_blocking_plot_prefix}${suffix}.out"
done
