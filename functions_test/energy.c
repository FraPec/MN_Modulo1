#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"

#define L 10

double energy_per_site(DoubleVector2D ***lattice, int lattice_side) {
    int i, j, k, i_plus, j_plus, k_plus;
    int Vol = lattice_side * lattice_side * lattice_side;
    double energy_per_site = 0.0;
    DoubleVector2D S_nearest; S_nearest.sx = 0.0; S_nearest.sy = 0.0;

    for (i=0; i<lattice_side; i++) {
        for (j=0; j<lattice_side; j++) {
            for (k=0; k<lattice_side; k++) { 
		// Periodic boudary conditions
		// Only sites after the one we are considering are included, to avoid double counting
                i_plus  = (i + 1) % lattice_side;
	        j_plus  = (j + 1) % lattice_side;
		k_plus  = (k + 1) % lattice_side;
       
		S_nearest.sx = lattice[i_plus][j][k].sx + lattice[i][j_plus][k].sx + lattice[i][j][k_plus].sx;
                S_nearest.sy = lattice[i_plus][j][k].sy + lattice[i][j_plus][k].sy + lattice[i][j][k_plus].sy;

		energy_per_site += - scalar_product(lattice[i][j][k], S_nearest) / (double) Vol;
            }
        }
    }

    return energy_per_site;
}

int main() {
    DoubleVector2D ***lattice;
    double a = 12.0, b = 0.0;
    int i, j, k;
    // Energy for O(2) with all parallel spins is E = - J * |a|^2 * sum_over_NN(cos(0)) = - J * 3 * |a|^2 * L^3 --> Per site with J=1: E = -3.0*|a|^2
    double obtained_energy, real_energy = - 3.0 * a * a;

    // Allocate lattice
    if (allocate(&lattice, L) == EXIT_FAILURE) {
        return EXIT_FAILURE;
    }

    // Setting values in the dynamically allocated lattice
    for (i=0; i<L; i++) {
        for (j=0; j<L; j++) {
            for (k=0; k<L; k++) {
                lattice[i][j][k].sx = a;
                lattice[i][j][k].sy = b;
            }
        }
    }
   
    obtained_energy = energy_per_site(lattice, L);
    if ((fabs(obtained_energy-real_energy)<1e-11)) {
        fprintf(stdout, "Test passed, energy is equal to theoretical value!\n");
        fprintf(stdout, "E = %.15lf, E_theory = %.15lf\n", obtained_energy, real_energy);
        return EXIT_SUCCESS;
    } else {
        fprintf(stdout, "Test failed, energy is NOT equal to theoretical value!\n");
        fprintf(stdout, "E = %.15lf, E_theory = %.15lf\n", obtained_energy, real_energy);
	return EXIT_SUCCESS;
    }

    return EXIT_SUCCESS;

}

