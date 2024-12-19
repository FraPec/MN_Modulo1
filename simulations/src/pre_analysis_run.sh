#!/bin/bash

# Check if both arguments are provided
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 executable.o num_procs"
    exit 1
fi

# Assign arguments to variables
executable="$1"
# Get the number of available processors
num_procs="$2"


beta_values=(0.3 0.4 0.5 0.6)
alpha_values=(0.001 0.01 0.1 1)
lattice_side_values=(10 20 30 40 50 60 70)
# Counter to track the number of running processes
proc_count=0

# Check and remove directories if they exist
[[ -d inputs ]] && rm -r inputs
[[ -d data ]] && rm -r data
[[ -d outputs ]] && rm -r outputs

# Create directories for input, data, and output files, together with all the lattice subdirectories
for lattice_side in "${lattice_side_values[@]}"; do
    mkdir -p inputs/lattice${lattice_side}
    mkdir -p data/lattice${lattice_side}
    mkdir -p outputs/lattice${lattice_side}
done


# Loop over each combination of beta, alpha, and lattice_side
for lattice_side in "${lattice_side_values[@]}"; do
    for beta in "${beta_values[@]}"; do
        for alpha in "${alpha_values[@]}"; do

            # Define filenames within their respective folders
            input_file="inputs/lattice${lattice_side}/input_b${beta}_a${alpha}_L${lattice_side}.in"
            data_file="data/lattice${lattice_side}/data_b${beta}_a${alpha}_L${lattice_side}.dat"
            output_file="outputs/lattice${lattice_side}/output_b${beta}_a${alpha}_L${lattice_side}.out"

            # Generate the input file for this run
            cat > "$input_file" <<EOF
lattice_side $lattice_side
sample 1000000   
output_data_format minimal
beta $beta
alpha $alpha
epsilon 0.2   
EOF

            # Run the simulation in the background, redirecting stdout to output file
            echo "Running simulation with beta=$beta, alpha=$alpha, lattice_side=$lattice_side"
            ./$executable "$input_file" "$data_file" > "$output_file" &

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
echo "Done."