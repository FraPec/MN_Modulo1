#!/bin/bash

# Set locale for correct numeric formatting
export LC_NUMERIC=C

# Check if both arguments are provided
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 executable.o num_procs"
    exit 1
fi

# Assign arguments to variables
executable="$1"
# Get the number of available processors
num_procs="$2"


# Total number of values
total_values=130
# Number of values in the specific range 0.43 to 0.47
specific_range_values=30

# Generate values in the specific range from 0.43 to 0.47
specific_start=0.43
specific_end=0.47
specific_step=$(echo "scale=5; ($specific_end - $specific_start) / ($specific_range_values - 1)" | bc)
specific_values=($(seq $specific_start $specific_step $specific_end))

# Calculate values outside the specific range
total_other_values=$((total_values - specific_range_values))

# Split other values into two parts: from 0.35 to just below 0.43 and from just above 0.47 to 0.55
other_start1=0.1
other_end1=0.429
other_start2=0.471
other_end2=0.8

# Calculate the number of values in each of these two other ranges
# We use ceiling approximation to ensure the total count matches 110
other_values1=$(echo "($total_other_values / 2)" | bc)
other_values2=$(($total_other_values - other_values1))

other_step1=$(echo "scale=5; ($other_end1 - $other_start1) / ($other_values1 - 1)" | bc)
other_step2=$(echo "scale=5; ($other_end2 - $other_start2) / ($other_values2 - 1)" | bc)

# Generate the other values
other_values1=($(seq $other_start1 $other_step1 $other_end1))
other_values2=($(seq $other_start2 $other_step2 $other_end2))

# Combine all values and sort
beta_values=(${other_values1[@]} ${specific_values[@]} ${other_values2[@]})
beta_values[$total_values - 1]=0.8

# Print combined and sorted beta values
echo "Combined and sorted beta values:"
echo "${beta_values[@]}"

alpha_values=1.0
lattice_side_values=(10 20 30 40 50)
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
            data_file="data/lattice${lattice_side}/data_b${beta}_a${alpha}_L${lattice_side}.bin"
            output_file="outputs/lattice${lattice_side}/output_b${beta}_a${alpha}_L${lattice_side}.out"

            # Generate the input file for this run
            cat > "$input_file" <<EOF
lattice_side $lattice_side
seed time
sample $((lattice_side * lattice_side * lattice_side * 30000))   
output_data_format minimal
beta $beta
alpha $alpha
epsilon 0.1 
printing_step $((lattice_side * lattice_side * lattice_side))
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
done

# Final wait to ensure all background processes complete
wait
echo "Done."
