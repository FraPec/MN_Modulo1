#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "../include/functions.h"
#include "../include/random.h"







int main() {
    int lattice_side = 30;   // Dimension of the 3D matrix
    double alpha = 1;     // Parameter to calculate theta
    double beta = 5000;      // Inverse of the temperature
    double s_mod;
    long unsigned int seed1 = time(NULL);
    long unsigned int seed2 = seed1 + 145367;

    myrand_init(seed1, seed2);

    // Matrix declaration and allocation
    DoubleVector2D ***lattice = allocate(lattice_side);

    // Checking allocation errors
    if (lattice == NULL) {
        fprintf(stderr, "Matrix allocation error.\n");
        return EXIT_FAILURE;
    }

    // Initializing the matrix
    initialize_lattice(lattice, lattice_side);

    // Testing the local_metropolis function on a specific site
    int i = 2, j = 2, k = 2;  // Indices of the site to update
    DoubleVector2D s_old = lattice[i][j][k];
    int acc = local_metropolis(lattice, i, j, k, lattice_side, alpha, beta);

    // Checking the result
    if (acc == 1) {
        double s_new_mod = sqrt(scalar_product(lattice[i][j][k], lattice[i][j][k]));
        printf("Update successful for lattice[%d][%d][%d]: sx_new = %.15lf, sy_new = %.15lf, s_new module = %.15lf\n",
               i, j, k, lattice[i][j][k].sx, lattice[i][j][k].sy, s_new_mod);
        double s_old_mod = sqrt(scalar_product(s_old, s_old));
        printf("Old state: sx_old = %.15lf, sy_old = %.15lf, s_old module = %.15lf\n", s_old.sx, s_old.sy, s_old_mod);
    } else {
        double s_new_mod = sqrt(scalar_product(lattice[i][j][k], lattice[i][j][k]));
        printf("Update not performed for lattice[%d][%d][%d]: sx_new = %.15lf, sy_new = %.15lf, s_new module = %.15lf\n",
               i, j, k, lattice[i][j][k].sx, lattice[i][j][k].sy, s_new_mod);
        double s_old_mod = sqrt(scalar_product(s_old, s_old));
        printf("Old state: sx_old = %.15lf, sy_old = %.15lf, s_old module = %.15lf\n", s_old.sx, s_old.sy, s_old_mod);
    }

    // Memory release
    free_lattice(lattice, lattice_side);

    return EXIT_SUCCESS;
}
