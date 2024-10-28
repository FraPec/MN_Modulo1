#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "../include/functions.h"

double scalar_product(DoubleVector2D s1, DoubleVector2D s2){
    double sc = 0.;
    sc = (s1.sx * s2.sx) + (s1.sy * s2.sy);

    return sc;
}

int microcanonical(DoubleVector2D *s, DoubleVector2D *S) {
     double sq_mod_S, sS_scal_prod;
     int i;

     sq_mod_S = scalar_product(*S, *S);
     if (sqrt(sq_mod_S)<1e-13) {
         return EXIT_FAILURE;
     } else {
 	sS_scal_prod = scalar_product(*s, *S);
 	s->sx = 2 * S->sx * sS_scal_prod / sq_mod_S - s->sx;
        s->sy = 2 * S->sy * sS_scal_prod / sq_mod_S - s->sy;
 	return EXIT_SUCCESS;
     }
}


int normalization(DoubleVector2D *s) {
// How many normalizations needed during a simulation?

     int i;
     double mod_s = sqrt(scalar_product(*s, *s));

     s->sx = s->sx / mod_s;
     s->sy = s->sy / mod_s;

     mod_s = sqrt(scalar_product(*s, *s));
     if (fabs(mod_s-1.0)<1e-15) {
         return EXIT_SUCCESS;
     } else {
         fprintf(stderr, "Renormalization of vector failed!\n");
         return EXIT_FAILURE;
     }
}




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
