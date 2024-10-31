#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "../include/functions.h"
#include "../include/random.h"

#define MAX_LENGTH 128

int main(int argc, char * argv[]) {
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
    // Trying to open the file give as output
    FILE *data = fopen(data_name, "w");
    if (data == NULL) {
        fprintf(stderr, "Error opening output file\n");
        fclose(inp_file);
        return EXIT_SUCCESS;
    }
    fprintf(stdout, "Input file name: %s\n", inp_file_name);
    fprintf(stdout, "Output file name: %s\n", data_name);


    /////////////////////////////////////////////////////////////////
    // Let's extract all the useful parameters from the input file //
    /////////////////////////////////////////////////////////////////
    int param_found = 0;
    char param_name[MAX_LENGTH], param_type[MAX_LENGTH];
    int lattice_side, sample;
    double beta, alpha, epsilon;
    fprintf(stdout, "### Parameters of the simulation:\n");
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
        fclose(data);
        return EXIT_SUCCESS;
    }
    // sample = number of data we want to collect
    strcpy(param_name, "sample");
    strcpy(param_type, "%d");
    param_found = read_parameter(inp_file, param_name, param_type, &sample);
    if (param_found==1) {
        fprintf(stdout, "%s = %d\n", param_name, sample);
    } else {
        fprintf(stdout, "%s has not been found in %s!\n", param_name, inp_file_name);
        fprintf(stdout, "Simulation aborted!\n");
        fclose(inp_file);
        fclose(data);
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
        fclose(data);
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
        fclose(data);
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
        fclose(data);
        return EXIT_SUCCESS;
    }

    /////////////////////////////
    // Initialize seed for rng //
    /////////////////////////////
    const unsigned long int seed1 = time(NULL);
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
    int step=0, Vol, i, j, k, l, m, n, metro=0, metro_acc=0, micro_acc=0, metro_steps=0, micro_steps=0;
    Vol = lattice_side * lattice_side * lattice_side;
    double random_n, E_per_site;
    char type_of_update[MAX_LENGTH];
    DoubleVector2D s_old, s_new, * magn;
    fprintf(data, "# step i j k sx_old sy_old sx_new sy_new mx my E type_of_update\n");




    while (step<sample) {
        if (step%Vol==0) {
            // random number generation after a complete update of the lattice
            random_n = myrand();
            if (random_n<epsilon) { // if such number is less than epsilon then the next L^3
                metro=1;  // steps are metropolis, otherwise they are microcanonical
                fprintf(stdout, "Next L^3 steps will be Metropolis!\n");
                strcpy(type_of_update, "metropolis");
            } else {
                metro=0; // microcanonical steps
                fprintf(stdout, "Next L^3 steps will be microcanonical!\n");
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
            fprintf(stdout, "Normalization has been performed!\n");
        }

        if(metro == 0){
            for (i=0; i<lattice_side; i++) {
                for (j=0; j<lattice_side; j++) {
                    for (k=0; k<lattice_side; k++) {
                        micro_steps += 1;
                        s_old = lattice[i][j][k];
                        micro_acc += microcanonical(lattice, i, j, k, lattice_side);
                        s_new = lattice[i][j][k];
                        E_per_site = energy_per_site(lattice, lattice_side);
                        magn = magnetization(lattice, lattice_side);
                        fprintf(data, "%d %d %d %d %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %s\n", step, i, j, k, s_old.sx, s_old.sy, s_new.sx, s_new.sy, magn->sx, magn->sy, E_per_site, type_of_update);
                        step +=1;
                    }
                }
            }
        }

        if(metro == 1){
            for (i=0; i<lattice_side; i++) {
                for (j=0; j<lattice_side; j++) {
                    for (k=0; k<lattice_side; k++) {
                        metro_steps += 1;
                        s_old = lattice[i][j][k];
                        metro_acc += local_metropolis(lattice, i, j, k, lattice_side, alpha, beta);
                        s_new = lattice[i][j][k];
                        E_per_site = energy_per_site(lattice, lattice_side);
                        magn = magnetization(lattice, lattice_side);
                        fprintf(data, "%d %d %d %d %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %s\n", step, i, j, k, s_old.sx, s_old.sy, s_new.sx, s_new.sy, magn->sx, magn->sy, E_per_site, type_of_update);
                        step +=1;
                    }
                }
            }
        }




        // // Generation of 3 random indexes to obtain lattice site
        // random_n = myrand();
        // i = (int) (lattice_side * random_n); // such operation works as a floor operation, not a round operation
        // random_n = myrand();
        // j = (int) (lattice_side * random_n);
        // random_n = myrand();
        // k = (int) (lattice_side * random_n);
        // s_old = lattice[i][j][k];

        // Microcanonical step
        // if (metro==0) {
        //     micro_steps += 1;
        //     micro_acc += microcanonical(lattice, i, j, k, lattice_side);
        // }
        // // Metropolis step
        // if (metro==1) {
        //     metro_steps += 1;
        //     metro_acc += local_metropolis(lattice, i, j, k, lattice_side, alpha, beta);
        // }
        // s_new = lattice[i][j][k];
        // E_per_site = energy_per_site(lattice, lattice_side);
        // magn = magnetization(lattice, lattice_side);
        // fprintf(data, "%d %d %d %d %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %.15lf %s\n", step, i, j, k, s_old.sx, s_old.sy, s_new.sx, s_new.sy, E_per_site, magn->sx, magn->sy, type_of_update);

    }






    fprintf(stdout, "\nSimulation ended.\nTotal steps: %d\n", sample);
    fprintf(stdout, "Metropolis steps performed, accepted and accepted/performed: %d, %d, %lf\n", metro_steps, metro_acc, (double)metro_acc / (double)metro_steps);
    fprintf(stdout, "Microcanonical steps performed and accepted: %d, %d\n", micro_steps, micro_acc);
    free_lattice(lattice, lattice_side);
    fclose(inp_file);
    fclose(data);
    return EXIT_SUCCESS;
}
