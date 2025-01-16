#!/bin/bash

# Set locale for correct numeric formatting
export LC_NUMERIC=C
scale=5 #scale for numerical precision
nu=0.6717
beta_c=0.4542
scaled_beta=0.6

# Check if both arguments are provided
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 executable.o num_procs"
    exit 1
fi

# Assign arguments to variables
executable="$1"
# Get the number of available processors
num_procs="$2"

# Sequence for lattice_side
lattice_side_values=(30) #27 24 21 18 15 12 9)
# Sequence for beta values
echo -e "chosen lattices: ${lattice_side_values[*]}"

# Counter to track the number of running processes
proc_count=0

# Parameters for the simulations
sample_size=20000000 # number of total sweeps for each lattice
printing_step=80 # complete lattice iterations between means computing (sampling)
alpha=1.0 # amplitude of the angle for Metropolis step
epsilon=0.1 # percentage of Metropolis w.r.t. Microcanonical 
number_betas=15

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
    # Creation of a custom beta array for the current lattice
    beta_down=$(echo "scale=$scale; $beta_c - $scaled_beta / (e(l($lattice_side) / $nu))" | bc -l)
    beta_up=$(echo "scale=$scale; $beta_c + $scaled_beta / (e(l($lattice_side) / $nu))" | bc -l)
    delta_beta=$(echo "scale=$scale; ($beta_up - $beta_down) / $number_betas" | bc -l)
    beta_values=()
    for i in $(seq 0 15); do
        beta=$(echo "scale=$scale; $beta_down + $i * $delta_beta" | bc -l)
        beta_values+=($beta)
    done
    echo "${beta_values[@]}"   
    for beta in "${beta_values[@]}"; do
        # Define filenames within their respective folders
        input_file="inputs/lattice${lattice_side}/input_b${beta}_L${lattice_side}.in"
        data_file="data/lattice${lattice_side}/data_b${beta}_L${lattice_side}.bin"
        output_file="outputs/lattice${lattice_side}/output_b${beta}_L${lattice_side}.out"
 
        # Generate the input file for this run
        cat > "$input_file" <<EOF
lattice_side $lattice_side
seed time
total_lattice_sweeps $sample_size
printing_step $printing_step
data_format binary
beta $beta
alpha $alpha
epsilon $epsilon
verbose false
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

# Final wait to ensure all background processes complete
wait
echo "Done."
