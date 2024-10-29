#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "../include/functions.h"
#include "../include/random.h"

#define MAX_LENGTH 128

int main(int argc, char * argv[]) {
    // Check if the number of parameters is 2, i.e. ./program file.txt
    if ((argc<2)&&(argc>3)) {
        fprintf(stdout, "Invalid input!\nHow to use this program:\n./program input.in // shell as output\n./program input.in output.out // output.out as output\n");
        return EXIT_SUCCESS;
    }

    char file_name[MAX_LENGTH];
    strcpy(file_name, argv[1]);

    // Trying to open the file give as input    
    FILE *file = fopen(file_name, "r"); 
    if (file == NULL) {
        fprintf(stderr, "Error opening input file\n");
        return EXIT_SUCCESS;
    }
    fprintf(stdout, "Input file name: %s\n", file_name); 

    // Trying to open output file, if given
    FILE *file_writing = stdout;
    if (argc==3) {
        file_writing = fopen(argv[2], "w");
        if (file == NULL) {
            fprintf(stderr, "Error opening output file\n");
            return EXIT_SUCCESS;
        }
        fprintf(stdout, "Output file name: %s\n\n", argv[2]);
    } else {
        fprintf(stdout, "Printing in stdout\n\n");
    }
    

      
    ////////////////////////////////////////////////////////////////
    // Let's extract all the useful parameters from the input.txt //
    ////////////////////////////////////////////////////////////////
    int param_found = 0;
    char param_name[MAX_LENGTH], param_type[MAX_LENGTH];
    int lattice_side, sample;
    double beta, alpha, epsilon;
    fprintf(file_writing, "### Parameters of the simulation:\n");
    // lattice_side = side of the 3D square lattice
    strcpy(param_name, "lattice_side");
    strcpy(param_type, "%d");
    param_found = read_parameter(file, param_name, param_type, &lattice_side);
    if (param_found==1) {
        fprintf(file_writing, "%s = %d\n", param_name, lattice_side);
    } else {
        fprintf(file_writing, "%s has not been found in %s!\n", param_name, file_name);
        fprintf(file_writing, "Simulation aborted!\n");
        return EXIT_SUCCESS;
    }
    // sample = number of data we want to collect
    strcpy(param_name, "sample");
    strcpy(param_type, "%d");
    param_found = read_parameter(file, param_name, param_type, &sample);
    if (param_found==1) {
        fprintf(file_writing, "%s = %d\n", param_name, sample);
    } else {
        fprintf(file_writing, "%s has not been found in %s!\n", param_name, file_name);
        fprintf(file_writing, "Simulation aborted!\n");
        fclose(file);
        fclose(file_writing);
        return EXIT_SUCCESS;
    }
    // beta = 1 / temperature
    strcpy(param_name, "beta");
    strcpy(param_type, "%lf");
    param_found = read_parameter(file, param_name, param_type, &beta);
    if (param_found==1) {
        fprintf(file_writing, "%s = %lf\n", param_name, beta);
    } else {
        fprintf(file_writing, "%s has not been found in %s!\n", param_name, file_name);
        fprintf(file_writing, "Simulation aborted!\n");
        fclose(file);
        fclose(file_writing);
        return EXIT_SUCCESS;
    }
    // alpha = angle for the metropolis step, new_theta~unif(-alpha + theta, alpha + theta): new s(theta) = s(ne_theta)
    strcpy(param_name, "alpha");
    strcpy(param_type, "%lf");
    param_found = read_parameter(file, param_name, param_type, &alpha);
    if (param_found==1) {
        fprintf(file_writing, "%s = %lf\n", param_name, alpha);
    } else {
        fprintf(file_writing, "%s has not been found in %s!\n", param_name, file_name);
        fprintf(file_writing, "Simulation aborted!\n");
        fclose(file);
        fclose(file_writing);
        return EXIT_SUCCESS;
    }
    // epsilon = probability of perfoming L^3 metropolis update; (1-epsilon) is the prob. of performing L^3 microcan. updates 
    strcpy(param_name, "epsilon");
    strcpy(param_type, "%lf");
    param_found = read_parameter(file, param_name, param_type, &epsilon);
    if (param_found==1) {
        fprintf(file_writing, "%s = %lf\n", param_name, epsilon);
    } else {
        fprintf(file_writing, "%s has not been found in %s!\n", param_name, file_name);
        fprintf(file_writing, "Simulation aborted!\n");
        fclose(file);
        fclose(file_writing);
        return EXIT_SUCCESS;
    }
   
    ///////////////////////////////////////////
    // Structure allocation & initialization //
    ///////////////////////////////////////////
    DoubleVector2D *** lattice = allocate(lattice_side);
    if (lattice==NULL) {
        fprintf(file_writing, "Failed lattice structure allocation, simulation aborted!\n");
        fclose(file);
        fclose(file_writing);
        return EXIT_SUCCESS;
    }
    if (initialize_lattice(lattice, lattice_side)==EXIT_SUCCESS) {
        fprintf(file_writing, "Correctly allocated and randomly inizialized lattice\n");
    } else {
        fprintf(file_writing, "Failed randomly inizialization of lattice, simulation aborted!\n");
        fclose(file);
        fclose(file_writing); 
        return EXIT_SUCCESS;
    }
    

    ////////////////////////////////////
    // Let's start with the for cicle //
    ////////////////////////////////////
    
    int step, Vol, i=0, j=0, k=0;
    Vol = lattice_side * lattice_side * lattice_side;
    double random_from_unif;
    for (step=0; step<sample; step++) {
        if (step%Vol==0) {
            
        }
    }


    fclose(file);   
    fclose(file_writing);
    return EXIT_SUCCESS;
}


