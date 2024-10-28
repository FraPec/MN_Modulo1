#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"

#define L 10


int main() {
    DoubleVector2D ***lattice = allocate(L);
    double a = 12.0, b = 0.0;
    int i, j, k;
    // Energy for O(2) with all parallel spins is E = - J * |a|^2 * sum_over_NN(cos(0)) = - J * 3 * |a|^2 * L^3 --> Per site with J=1: E = -3.0*|a|^2
    double obtained_energy, real_energy = - 3.0 * a * a;

    // Allocate lattice
    if (lattice == NULL) {
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

