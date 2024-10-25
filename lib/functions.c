#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "../include/functions.h"

int print_vector(double * x, int len_x) {
    int i;
    for (i=0; i<len_x; i++) {
        fprintf(stdout, "%.14lf ", x[i]);
    }
    fprintf(stdout, "\n");
    return EXIT_SUCCESS;
}


double scalar_product(DoubleVector2D s1, DoubleVector2D s2){
    double sc = 0.;
    sc = (s1.sx * s2.sx) + (s1.sy * s2.sy);

    return sc;
}

// MICROCANONICAL E' DA RISCRIVERE
// int microcanonical(double *s, double *S, int len_s) {
//     double sq_mod_S, sS_scal_prod;
//     int i;
//
//     sq_mod_S = scalar_product(S, S, len_s);
//     if (sqrt(sq_mod_S)<1e-13) {
//         return EXIT_FAILURE;
//     } else {
// 	sS_scal_prod = scalar_product(s, S, len_s);
// 	for (i=0; i<len_s; i++) {
// 	    s[i] = 2 * S[i] * sS_scal_prod / sq_mod_S - s[i];
// 	}
// 	return EXIT_SUCCESS;
//     }
// }


// NORMALIZATION E' DA RISCRIVERE
// int normalization(double * r, int len_r) {
// // How many normalizations needed during a simulation?
//
//     int i;
//     double mod_r = sqrt(scalar_product(r, r, len_r));
//
//     for (i=0; i<len_r; i++) {
//         r[i] = r[i] / mod_r;
//     }
//
//     mod_r = sqrt(scalar_product(r, r, len_r));
//     if (fabs(mod_r-1.0)<1e-15) {
//         return EXIT_SUCCESS;
//     } else {
//         fprintf(stderr, "Renormalization of vector failed!\n");
//         return EXIT_FAILURE;
//     }
// }




// Function to free the memory of a 3D lattice of DoubleVector2D structures
void free_lattice(DoubleVector2D ***lattice, int lattice_side) {
    int i, j;
    // Loop through each level to free memory in reverse order of allocation
    for (i=0; i<lattice_side; i++) {
        for (j=0; j<lattice_side; j++) {
            free(lattice[i][j]); //Free each DoubleVector2D array at the third level
        }
        free(lattice[i]); //Free each DoubleVector2D* array at the second level
    }
    free(lattice); //Free the main array of DoubleVector2D**
}





// Function to allocate a 3D lattice of DoubleVector2D structures
DoubleVector2D ***allocate(int lattice_side) {
    DoubleVector2D ***lattice;
    int i, j, l;

    // First level allocation - array of pointers to arrays of pointers
    lattice = (DoubleVector2D ***)malloc(lattice_side * sizeof(DoubleVector2D **));
    if (lattice == NULL) {
        fprintf(stderr, "Error in the allocation of the first level.\n");
        return NULL;  // Return NULL if the allocation fails
    }

    // Second level allocation - for each pointer, allocate an array of DoubleVector2D pointers
    for (i = 0; i < lattice_side; i++) {
        lattice[i] = (DoubleVector2D **)malloc(lattice_side * sizeof(DoubleVector2D *));
        if (lattice[i] == NULL) {
            fprintf(stderr, "Error in the allocation of the second level.\n");

            // Free previously allocated memory in case of failure
            for (int k = 0; k < i; k++) {
                free(lattice[k]);
            }
            free(lattice);
            return NULL;  // Return NULL if allocation fails at this level
        }

        // Third level allocation - for each DoubleVector2D pointer, allocate the array of structures
        for (j = 0; j < lattice_side; j++) {
            lattice[i][j] = (DoubleVector2D *)malloc(lattice_side * sizeof(DoubleVector2D));
            if (lattice[i][j] == NULL) {
                fprintf(stderr, "Error in the allocation of the third level.\n");

                // Free the allocated memory at the current level
                for (l = 0; l < j; l++) {
                    free(lattice[i][l]);
                }
                free(lattice[i]);

                // Free memory allocated in previous levels
                for (int k = 0; k < i; k++) {
                    for (l = 0; l < lattice_side; l++) {
                        free(lattice[k][l]);
                    }
                    free(lattice[k]);
                }
                free(lattice);
                return NULL;  // Return NULL if allocation fails at this level
            }
        }
    }
    return lattice;  // Return the allocated 3D lattice
}
