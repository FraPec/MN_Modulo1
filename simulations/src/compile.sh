#!/bin/bash

# Check if a file was provided as an argument
if [ -z "$1" ]; then
    echo "Usage: ./compile.sh file_to_compile.c"
    exit 1
fi

# Get the filename without the extension
filename="${1%.*}"

# Compile the file with optimization flags and all the useful libraries
gcc -o "$filename".o "$1" ../lib/functions.c ../lib/random.c ../lib/pcg32min.c -O3 -march=native -mtune=native -flto -funroll-loops -fstrict-aliasing -ffast-math -lm

# Check if the compilation was successful
if [ $? -eq 0 ]; then
    echo "Compilation successful: $filename.o"
else
    echo "Compilation failed."
    exit 1
fi
