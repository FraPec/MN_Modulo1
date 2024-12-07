#!/bin/bash

# Check if the correct number of arguments is provided
# Usage: ./script.sh <input_folder> <output_folder> <file_txt> <max_block_size> <num_procs>
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <input_folder> <output_folder> <file_txt> <max_block_size> <num_procs>"
    exit 1
fi

# Get input parameters from command-line arguments
INPUT_FOLDER="$1"          # Directory containing input files
OUTPUT_FOLDER="$2"         # Directory to save output files
FILE_TXT="$3"              # Additional text file used by the Python script
MAX_BLOCK_SIZE="$4"        # Max block size
NUM_PROCS="$5"             # Number of processes to run in parallel

rm -f "$FILE_TXT"    # Remove the file if it exists
echo "# variable_name mean variace beta" > "$FILE_TXT"
rm -f "$OUTPUT_FOLDER/*"

echo "INPUT_FOLDER: $INPUT_FOLDER"
echo "OUTPUT_FOLDER: $OUTPUT_FOLDER"
echo "FILE_TXT: $FILE_TXT"
echo "MAX_BLOCK_SIZE: $MAX_BLOCK_SIZE"
echo "NUM_PROCS: $NUM_PROCS"

# Create the output folder if it does not exist
mkdir -p "$OUTPUT_FOLDER"

# Define a function to process a single input file
process_file() {
    local input_file="$1"              # Path to the input file
    local base_name=$(basename "$input_file")  # Extract filename from the full path
    local output_file="$OUTPUT_FOLDER/$base_name"  # Define the output file path

    # Run the Python script with required arguments
    python3 blocking_plot.py --input_datafile "$input_file" \
                             --plot_name "$output_file" \
                             --max_block_size "$MAX_BLOCK_SIZE" \
                             --txt_file "$FILE_TXT"

    # Check the exit status of the Python script and log the result
    if [ $? -eq 0 ]; then
        echo "Processed $input_file -> $output_file"
    else
        echo "Error processing $input_file"
    fi
}

# Export the function and required variables for parallel execution
export -f process_file                # Make process_file function accessible to parallel
export OUTPUT_FOLDER FILE_TXT         # Share these variables with parallel processes

# Use GNU `parallel` to process all files in the input folder concurrently
# -j "$NUM_PROCS" specifies the number of parallel jobs
find "$INPUT_FOLDER" -type f | parallel -j "$NUM_PROCS" \
    "python3 blocking_plot.py --input_datafile {} \
                              --plot_name $OUTPUT_FOLDER/{/} \
                              --max_block_size $MAX_BLOCK_SIZE \
                              --txt_file $FILE_TXT"

