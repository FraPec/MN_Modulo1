#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_folder> <output_folder>"
    exit 1
fi

# Get the input and output folder paths from arguments
INPUT_FOLDER="$1"
OUTPUT_FOLDER="$2"

# Create output folder if it doesn't exist
mkdir -p "$OUTPUT_FOLDER"

# Loop through all files in the input folder
for input_file in "$INPUT_FOLDER"/*; do
    # Get the filename without the path
    base_name=$(basename "$input_file")
    
    # Define the output file path
    output_file="$OUTPUT_FOLDER/$base_name"

    # Run the Python script for each file
    python3 blocking_plot.py --input_datafile "$input_file" --plot_name "$output_file" --max_block_size 10000 --txt_file file.txt

    # Check if the script executed successfully
    if [ $? -eq 0 ]; then
        echo "Processed $input_file -> $output_file"
    else
        echo "Error processing $input_file"
    fi
done
