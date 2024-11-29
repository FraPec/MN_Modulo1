#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "../include/functions.h"
#include "../include/random.h"

#define MAX_LENGTH 128

int main(int argc, char * argv[]) {
    clock_t t_start, t_end;
    double cpu_time_used;
    t_start = clock();
    
    // Check if the number of parameters is 3, i.e. ./program inputfile.in data.dat
    if (argc!=3) {
        fprintf(stdout, "Invalid input!\nHow to use this program:\n./program input.in datafile\n");
        return EXIT_SUCCESS;
    }

    char inp_file_name[MAX_LENGTH], data_name[MAX_LENGTH];
    strcpy(inp_file_name, argv[1]);
    strcpy(data_name, argv[2]);

    //////////////////////////////
    // Opening input and output //
    //////////////////////////////
    // Trying to open the file give as input
    FILE *inp_file = fopen(inp_file_name, "r");
    if (inp_file == NULL) {
        fprintf(stderr, "Error opening input file\n");
        return EXIT_SUCCESS;
    }
    fprintf(stdout, "Input file name: %s\n", inp_file_name);

    /////////////////////////////////////////////////////////////////
    // Let's extract all the useful parameters from the input file //
    /////////////////////////////////////////////////////////////////
    int param_found = 0;
    char param_name[MAX_LENGTH], param_type[MAX_LENGTH], verbose[MAX_LENGTH];
    unsigned long int sample;
    int lattice_side, printing_step;
    double beta, alpha, epsilon;
    char data_format[MAX_LENGTH], seed[MAX_LENGTH];
    fprintf(stdout, "### Parameters of the simulation:\n");
    // Type of data format of the output .dat file
    strcpy(param_name, "output_data_format");
    strcpy(param_type, "%s");
    param_found = read_parameter(inp_file, param_name, param_type, &data_format);
    if (param_found==1) {
        fprintf(stdout, "%s = %s\n", param_name, data_format);
        if (strcmp(data_format, "minimal")!=0 && strcmp(data_format, "complete")!=0) {
            fprintf(stdout, "Invalid type of format choosen for the file! Valid keywords: 'minimal' and 'complete'.\n");
            fprintf(stdout, "Simulation aborted!\n");
            fclose(inp_file);
            return EXIT_SUCCESS;
        }
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // Type of verbosity
    strcpy(param_name, "verbose");
    strcpy(param_type, "%s");
    param_found = read_parameter(inp_file, param_name, param_type, &verbose);
    if (param_found==1) {
        fprintf(stdout, "%s = %s\n", param_name, verbose);
        if (strcmp(verbose, "true")!=0 && strcmp(verbose, "false")!=0) {
            fprintf(stdout, "Invalid type of verbosity choosen for the file! Valid keywords: 'true' and 'false'.\n");
            fprintf(stdout, "Simulation aborted!\n");
            fclose(inp_file);
            return EXIT_SUCCESS;
        }
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    
    // lattice_side = side of the 3D square lattice
    strcpy(param_name, "lattice_side");
    strcpy(param_type, "%d");
    param_found = read_parameter(inp_file, param_name, param_type, &lattice_side);
    if (param_found==1) {
        fprintf(stdout, "%s = %d\n", param_name, lattice_side);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // sample = number of data we want to collect
    strcpy(param_name, "sample");
    strcpy(param_type, "%lu");
    param_found = read_parameter(inp_file, param_name, param_type, &sample);
    if (param_found==1) {
        fprintf(stdout, "%s = %lu\n", param_name, sample);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // beta = 1 / temperature
    strcpy(param_name, "beta");
    strcpy(param_type, "%lf");
    param_found = read_parameter(inp_file, param_name, param_type, &beta);
    if (param_found==1) {
        fprintf(stdout, "%s = %lf\n", param_name, beta);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // alpha = angle for the metropolis step, new_theta~unif(-alpha + theta, alpha + theta): new s(theta) = s(ne_theta)
    strcpy(param_name, "alpha");
    strcpy(param_type, "%lf");
    param_found = read_parameter(inp_file, param_name, param_type, &alpha);
    if (param_found==1) {
        fprintf(stdout, "%s = %lf\n", param_name, alpha);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // epsilon = probability of perfoming L^3 metropolis update; (1-epsilon) is the prob. of performing L^3 microcan. updates
    strcpy(param_name, "epsilon");
    strcpy(param_type, "%lf");
    param_found = read_parameter(inp_file, param_name, param_type, &epsilon);
    if (param_found==1) {
        fprintf(stdout, "%s = %lf\n", param_name, epsilon);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // printing_step = number of step of printing in the file
    strcpy(param_name, "printing_step");
    strcpy(param_type, "%d");
    param_found = read_parameter(inp_file, param_name, param_type, &printing_step);
    if (param_found==1) {
        fprintf(stdout, "%s = %d\n", param_name, printing_step);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // seed = seed for rng, can be choosen to be time or a custom number to make simulation reproducible
    unsigned long int seed1; strcpy(param_name, "seed");
    strcpy(param_type, "%s");
    param_found = read_parameter(inp_file, param_name, param_type, &seed);
    if (param_found==1) {
        fprintf(stdout, "%s = %s\n", param_name, seed);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    if (strcmp(seed, "time")==0) {
        seed1 = (const unsigned long int)time(NULL);
    } else { // Everything else other than the keyword "time" is converted to a long unsigned int, so be careful
        seed1 = (const unsigned long int)atoi(seed);
    }

    //////////////////////////////////////////////////////////////////
    // Opening data file in which simulation is going to be written //
    //////////////////////////////////////////////////////////////////
    // Trying to open the file give as output
    FILE * data;
    if (strcmp(data_format, "complete")==0) {
	data = fopen(data_name, "w"); // we are choosing to write in a human readible file
    }
    if (strcmp(data_format, "minimal")==0) {
        data = fopen(data_name, "wb"); // we are choosing to write in a binary
    }
    if (data == NULL) {
        fprintf(stderr, "Error opening output data file\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    
    fprintf(stdout, "Data file name: %s\n", data_name);
    /////////////////////////////
    // Initialize seed for rng //
    /////////////////////////////
    const unsigned long int seed2 = seed1 + 137;
    fprintf(stdout, "Current seeds: %d, %d\n", (int)seed1, (int)seed2);
    myrand_init(seed1, seed2);

    ///////////////////////////////////////////
    // Structure allocation & initialization //
    ///////////////////////////////////////////
    DoubleVector2D *** lattice = allocate(lattice_side);
    if (lattice==NULL) {
        fprintf(stdout, "Failed lattice structure allocation, simulation aborted!\n");
        fclose(inp_file);
        fclose(data);
        return EXIT_SUCCESS;
    }
    if (initialize_lattice(lattice, lattice_side)==EXIT_SUCCESS) {
        fprintf(stdout, "Correctly allocated and randomly inizialized lattice\n");
    } else {
        fprintf(stdout, "Failed randomly inizialization of lattice, simulation aborted!\n");
        fclose(inp_file);
        fclose(data);
        free_lattice(lattice, lattice_side);
        return EXIT_SUCCESS;
    }

    ////////////////////////////////////
    // Let's start with the for cicle //
    ////////////////////////////////////
    unsigned long int step=0, metro_acc=0, micro_acc=0, metro_steps=0, micro_steps=0;
    int Vol, i, j, k, l, m, n, metro=0;
    Vol = lattice_side * lattice_side * lattice_side;
    double random_n, E_per_site;
    char type_of_update[MAX_LENGTH];
    DoubleVector2D s_old, s_new, * magn;
    if (strcmp(data_format, "complete")==0) {
        fprintf(data, "# step i j k sx_old sy_old sx_new sy_new mx my Energy_per_site\n");
    } 

    for (step=0; step<sample; step++) {
        if (step%Vol==0) {
            // random number generation after a complete update of the lattice
            random_n = myrand();
            if (random_n<epsilon) { // if such number is less than epsilon then the next L^3
                metro=1;  // steps are metropolis, otherwise they are microcanonical
	        if (strcmp(verbose, "true")==0) {
                    fprintf(stdout, "Next L^3 steps will be Metropolis!\n");
                }
                strcpy(type_of_update, "metropolis");
            } else {
                metro=0; // microcanonical steps
	        if (strcmp(verbose, "true")==0) {
                    fprintf(stdout, "Next L^3 steps will be microcanonical!\n");
                }
                strcpy(type_of_update, "microcanonical");
            }
            // normalization of all the sites after a complete update of the lattice
            for (l=0; l<lattice_side; l++) {
                for (m=0; m<lattice_side; m++) {
                    for (n=0; n<lattice_side; n++) {
                        normalization(&lattice[l][m][n]);
                    }
                }
            }
	    if (strcmp(verbose, "true")==0) {
                fprintf(stdout, "Normalization has been performed!\n");
            }
        }
        // Generation of 3 random indexes to obtain lattice site
        random_n = myrand();
        i = (int) (lattice_side * random_n); // such operation works as a floor operation, not a round operation
        random_n = myrand();
        j = (int) (lattice_side * random_n);
        random_n = myrand();
        k = (int) (lattice_side * random_n);
        s_old = lattice[i][j][k];

        // Microcanonical step
        if (metro==0) {
            micro_steps += 1;
            micro_acc += microcanonical(lattice, i, j, k, lattice_side);
        }
        // Metropolis step
        if (metro==1) {
            metro_steps += 1;
            metro_acc += local_metropolis(lattice, i, j, k, lattice_side, alpha, beta);
        }
        s_new = lattice[i][j][k];
	if (step%printing_step==0) {
            E_per_site = energy_per_site(lattice, lattice_side);
            magn = magnetization(lattice, lattice_side);
            if (strcmp(data_format, "complete")==0) {
                fprintf(data, "%lu %d %d %d %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %s\n", step, i, j, k, s_old.sx, s_old.sy, s_new.sx, s_new.sy, magn->sx, magn->sy, E_per_site, type_of_update);
            }
            if (strcmp(data_format, "minimal")==0) {
	        // To write in a binary we use fwrite()
                fwrite(&magn->sx, sizeof(double), 1, data);
	        fwrite(&magn->sy, sizeof(double), 1, data);
	        fwrite(&E_per_site, sizeof(double), 1, data);
	    }
        }
    }
    fprintf(stdout, "\nSimulation ended.\nTotal steps: %lu\n", sample);
    fprintf(stdout, "Metropolis steps performed, accepted and accepted/performed: %lu, %lu, %lf\n", metro_steps, metro_acc, (double)metro_acc / (double)metro_steps);
    fprintf(stdout, "Microcanonical steps performed and accepted: %lu, %lu\n", micro_steps, micro_acc);
    free_lattice(lattice, lattice_side);
    fclose(inp_file);
    fclose(data);
    t_end = clock();
    cpu_time_used = ((double) (t_end - t_start)) / CLOCKS_PER_SEC;
    fprintf(stdout, "Runtime of the last simulation: %.10lf\n", cpu_time_used);
    return EXIT_SUCCESS;
}
