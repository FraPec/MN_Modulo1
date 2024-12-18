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
        fprintf(stdout, "Invalid input!\nHow to use this program:\n./program input.inp datafile(.dat or .bin)\n");
	fprintf(stdout, "Input.inp must be like (do not include ' '):\nlattice_side int\nseed int or 'time'\ntotal_lattice_sweeps int\nprinting_step int\ndata_format 'binary' or 'text'\nbeta double\nalpha double\nepsilon double\nverbose 'false' or 'true'\n");
        return EXIT_SUCCESS;
    }

    char inp_file_name[MAX_LENGTH], data_name[MAX_LENGTH];
    strcpy(inp_file_name, argv[1]);
    strcpy(data_name, argv[2]);

    ///////////////////////////////////////////////////////////////
    // Opening input file from which inputs parameters are taken //
    ///////////////////////////////////////////////////////////////
    // Trying to open the file given as input
    FILE *inp_file = fopen(inp_file_name, "r");
    if (inp_file == NULL) {
        fprintf(stderr, "Error opening input file\n");
        return EXIT_SUCCESS;
    }
    fprintf(stdout, "Parameters input file name: %s\n", inp_file_name);

    /////////////////////////////////////////////////////////////////
    // Let's extract all the useful parameters from the input file //
    /////////////////////////////////////////////////////////////////
    int param_found = 0;
    char param_name[MAX_LENGTH], param_type[MAX_LENGTH];
    char data_format[MAX_LENGTH], seed[MAX_LENGTH], verbose[MAX_LENGTH];
    unsigned long int total_lattice_sweeps, printing_step;
    int lattice_side;
    double beta, alpha, epsilon;
    fprintf(stdout, "### Parameters of the simulation:\n");
    // Type of data format of the output .dat file
    strcpy(param_name, "data_format");
    strcpy(param_type, "%s");
    param_found = read_parameter(inp_file, param_name, param_type, &data_format);
    if (param_found==1) {
        fprintf(stdout, "%s = %s\n", param_name, data_format);
        if (strcmp(data_format, "binary")!=0 && strcmp(data_format, "text")!=0) {
            fprintf(stdout, "Invalid type of format choosen for the file! Valid keywords: 'binary' and 'text'.\n");
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
    // total_lattice_sweeps = number of complete sweeps of the lattice we want to collect
    strcpy(param_name, "total_lattice_sweeps");
    strcpy(param_type, "%lu");
    param_found = read_parameter(inp_file, param_name, param_type, &total_lattice_sweeps);
    if (param_found==1) {
        fprintf(stdout, "%s = %lu\n", param_name, total_lattice_sweeps);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    // printing_step = number of complete sweeps after which we want to compute and collect E and |m|
    strcpy(param_name, "printing_step");
    strcpy(param_type, "%lu");
    param_found = read_parameter(inp_file, param_name, param_type, &printing_step);
    if (param_found==1) {
        fprintf(stdout, "%s = %lu\n", param_name, printing_step);
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
    // seed = seed for rng, can be choosen to be time or a custom number to make simulation reproducible
    unsigned long int seed1; 
    strcpy(param_name, "seed");
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
    if (strcmp(data_format, "text")==0) {
	data = fopen(data_name, "w"); // we are choosing to write in a human readible file
    }
    if (strcmp(data_format, "binary")==0) {
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
    unsigned long int complete_lattice_sweeps=0, micro_acc=0, metro_acc=0, metro_steps=0, micro_steps=0;
    unsigned long int micro_full_lattice=0, metro_full_lattice=0;
    int Vol, i, j, k, l, m, n, metro=0;
    Vol = lattice_side * lattice_side * lattice_side;
    double random_n, E_per_site;
    double percentage_micro_acc = 0.0, percentage_metro_acc = 0.0; // Mean percentage of acceptance for micro and metro 
    DoubleVector2D s_old, s_new, * magn;
    if (strcmp(data_format, "text")==0) {
        fprintf(data, "# mx my Energy_per_site\n");
    } 

    while (complete_lattice_sweeps<total_lattice_sweeps) {
	// random number generation after a complete update of the lattice
	random_n = myrand();
	if (random_n<epsilon) { // if such number is less than epsilon then the next L^3
	    metro=1;  // steps are metropolis, otherwise they are microcanonical
	    if (strcmp(verbose, "true")==0) {
	        fprintf(stdout, "Next L^3 steps will be Metropolis!\n");
	    }
	} else {
	    metro=0; // microcanonical steps
	    if (strcmp(verbose, "true")==0) {
	        fprintf(stdout, "Next L^3 steps will be microcanonical!\n");
	    }
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

        if(metro == 0){
	    micro_full_lattice += 1;
	    micro_steps = 0;
	    micro_acc = 0;
            for (i=0; i<lattice_side; i++) {
                for (j=0; j<lattice_side; j++) {
                    for (k=0; k<lattice_side; k++) {
                        s_old = lattice[i][j][k];
                        micro_acc += microcanonical(lattice, i, j, k, lattice_side);
                        micro_steps += 1;
                        s_new = lattice[i][j][k];
                    }
                }
            }
	    percentage_micro_acc += (double)micro_acc / (double)micro_steps;
	    complete_lattice_sweeps += 1;
	    if (complete_lattice_sweeps%printing_step==0) {
                E_per_site = energy_per_site(lattice, lattice_side);
		magn = magnetization(lattice, lattice_side);
		if (strcmp(data_format, "text")==0) {
		    fprintf(data, "%.15lf %.15lf %.15lf\n", magn->sx, magn->sy, E_per_site);
		}
		if (strcmp(data_format, "binary")==0) {
		    // To write in a binary we use fwrite()
		    fwrite(&magn->sx, sizeof(double), 1, data);
		    fwrite(&magn->sy, sizeof(double), 1, data);
		    fwrite(&E_per_site, sizeof(double), 1, data);
		}
	    }
        }

        if(metro == 1){
	    metro_full_lattice += 1;
	    metro_steps = 0;
	    metro_acc = 0;
            for (i=0; i<lattice_side; i++) {
                for (j=0; j<lattice_side; j++) {
                    for (k=0; k<lattice_side; k++) {
                        s_old = lattice[i][j][k];
                        metro_acc += local_metropolis(lattice, i, j, k, lattice_side, alpha, beta);
                        metro_steps += 1;
                        s_new = lattice[i][j][k];
                    }
                }
            }
	    percentage_metro_acc += (double)metro_acc / (double)metro_steps;
            complete_lattice_sweeps += 1;
	    if (complete_lattice_sweeps%printing_step==0) {
                E_per_site = energy_per_site(lattice, lattice_side);
		magn = magnetization(lattice, lattice_side);
		if (strcmp(data_format, "text")==0) {
		    fprintf(data, "%.15lf %.15lf %.15lf\n", magn->sx, magn->sy, E_per_site);
		}
		if (strcmp(data_format, "binary")==0) {
		    // To write in a binary we use fwrite()
		    fwrite(&magn->sx, sizeof(double), 1, data);
		    fwrite(&magn->sy, sizeof(double), 1, data);
		    fwrite(&E_per_site, sizeof(double), 1, data);
		}
	    }
	}
    }

    fprintf(stdout, "\nSimulation ended.\nTotal steps: %lu\n", complete_lattice_sweeps);
    fprintf(stdout, "Metropolis complete sweeps of the lattice performed: %lu\nMean of the percentage of acceptance for Metropolis: %lf\n", metro_full_lattice, percentage_metro_acc / (double)metro_full_lattice);
    fprintf(stdout, "Microcanonical complete sweeps of the lattice performed: %lu\nMean of the percentage of acceptance for Microcanonical: %lf\n", micro_full_lattice, percentage_micro_acc / (double)micro_full_lattice);
    free_lattice(lattice, lattice_side);
    fclose(inp_file);
    fclose(data);
    t_end = clock();
    cpu_time_used = ((double) (t_end - t_start)) / CLOCKS_PER_SEC;
    fprintf(stdout, "Runtime of the last simulation: %.10lf\n", cpu_time_used);
    return EXIT_SUCCESS;
}
