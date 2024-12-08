#!/bin/bash

# Base input and output paths for blocking
input_blocking="data/lattice"
output_blocking_prefix="blocked_data/lattice"
log_blocking_prefix="blocking_lattice"

# Base paths for blocking plot
input_plot_prefix="blocked_data/lattice"
output_plot_prefix="plots/lattice"
sigma_output_prefix="sigma_outputs/lattice"
log_blocking_plot_prefix="blocking_plot_lattice"

# Loop through the desired suffixes
for suffix in 10 20 30 40 50; do
    # Run the blocking script
    ./blocking.sh "${input_blocking}${suffix}" "${output_blocking_prefix}${suffix}" > "${log_blocking_prefix}${suffix}.out"

    # Run the blocking plot script
    ./blocking_plot.sh "${input_plot_prefix}${suffix}" "${output_plot_prefix}${suffix}" "${sigma_output_prefix}${suffix}.txt" 1000 8 > "${log_blocking_plot_prefix}${suffix}.out"
done
