#!/bin/bash

# Define the range of each parameter
beta_values=(0.3 0.4) #(0.3 0.4 0.5 0.6)          
alpha_values=0.2 #(0.001 0.01 0.1 1.0)        
lattice_side_values=20 #(20 30 40)     

# Get the number of available processors
num_procs=2

# Counter to track the number of running processes
proc_count=0

# Create directories for input, data, and output files
mkdir -p inputs data outputs

# Loop over each combination of beta, alpha, and lattice_side
for beta in "${beta_values[@]}"; do
    for alpha in "${alpha_values[@]}"; do
        for lattice_side in "${lattice_side_values[@]}"; do
            
            # Define filenames within their respective folders
            input_file="inputs/input_beta${beta}_alpha${alpha}_lattice${lattice_side}.in"
            data_file="data/data_beta${beta}_alpha${alpha}_lattice${lattice_side}.dat"
            output_file="outputs/output_beta${beta}_alpha${alpha}_lattice${lattice_side}.out"

            # Generate the input file for this run
            cat > "$input_file" <<EOF
lattice_side $lattice_side
sample 100000    # Adjust the number of steps as desired
beta $beta
alpha $alpha
epsilon 0.2    # Adjust epsilon as needed
EOF

            # Run the simulation in the background, redirecting stdout to output file
            echo "Running simulation with beta=$beta, alpha=$alpha, lattice_side=$lattice_side"
            ./o2_metro_det.o "$input_file" "$data_file" > "$output_file" &

            # Increment the process counter
            ((proc_count++))

            # If the number of running processes equals the number of processors, wait for them to complete
            if (( proc_count == num_procs )); then
                wait            # Waits for all background processes to finish
                proc_count=0    # Reset process counter after waiting
            fi
        done
    done
done

# Final wait to ensure all background processes complete
wait
echo "All simulations have completed."


