#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "../include/functions.h"
#include "../include/random.h"

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

DoubleVector2D* magnetization(DoubleVector2D ***lattice, int lattice_side) {
    DoubleVector2D* m = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));
    int Vol = lattice_side * lattice_side * lattice_side; // faster and more accurate than pow (math.h) for integers!
    if (m==NULL) {
        fprintf(stderr, "Failed allocation for vector magnetization, returning NULL!\n");
        return NULL;
    }
    m->sx = 0.0; m->sy = 0.0;
    int i, j, k;

    for (i=0; i<lattice_side; i++) {
        for (j=0; j<lattice_side; j++) {
            for (k=0; k<lattice_side; k++) {
                m->sx += lattice[i][j][k].sx;
                m->sy += lattice[i][j][k].sy;
            }
        }
    }

    m->sx /= Vol;
    m->sy /= Vol;

    return m;
}

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


// Initializes all matrix values with random values for sx and sy s.t module = 1
int initialize_lattice(DoubleVector2D ***lattice, int lattice_side) {
    double theta;
    for (int i = 0; i < lattice_side; i++) {
        for (int j = 0; j < lattice_side; j++) {
            for (int k = 0; k < lattice_side; k++) {
                theta = (2*myrand() - 1)*PI;
                lattice[i][j][k].sx = cos(theta);
                lattice[i][j][k].sy = sin(theta);
            }
        }
    }
    return EXIT_SUCCESS;
}

int local_metropolis(DoubleVector2D ***lattice, int i, int j, int k, int lattice_side, double alpha, double beta) {
    int i_minus, i_plus, j_minus, j_plus, k_minus, k_plus, acc=0;
    double t, theta, dE, w, y;
    DoubleVector2D s_old, s_trial, S_sum;

    // Checking index validity
    if (i < 0 || i >= lattice_side || j < 0 || j >= lattice_side || k < 0 || k >= lattice_side) {
        fprintf(stderr, "Invalid lattice indices: %d, %d, %d. Lattice side is %d \n", i, j, k, lattice_side);
        return EXIT_FAILURE;
    }

    // Calculating neighboring indices with periodic boundary conditions
    i_minus = (i - 1 + lattice_side) % lattice_side;
    i_plus  = (i + 1) % lattice_side;
    j_minus = (j - 1 + lattice_side) % lattice_side;
    j_plus  = (j + 1) % lattice_side;
    k_minus = (k - 1 + lattice_side) % lattice_side;
    k_plus  = (k + 1) % lattice_side;

    // Generating random number U([0,1)) and calculating theta
    t = myrand();
    theta = (2 * t - 1) * alpha;

    // Retrieving current spin values at the site
    s_old = lattice[i][j][k];

    // Generating trial state from the old one
    s_trial.sx = cos(theta) * s_old.sx + sin(theta) * s_old.sy;
    s_trial.sy = -sin(theta) * s_old.sx + cos(theta) * s_old.sy;

    // Calculating the sum of neighbors for sx and sy
    S_sum.sx = lattice[i_minus][j][k].sx + lattice[i_plus][j][k].sx +
               lattice[i][j_minus][k].sx + lattice[i][j_plus][k].sx +
               lattice[i][j][k_minus].sx + lattice[i][j][k_plus].sx;

    S_sum.sy = lattice[i_minus][j][k].sy + lattice[i_plus][j][k].sy +
               lattice[i][j_minus][k].sy + lattice[i][j_plus][k].sy +
               lattice[i][j][k_minus].sy + lattice[i][j][k_plus].sy;

    // Calculating dE (energy) between the trial configuration and the old one
    dE = -(scalar_product(s_trial, S_sum) - scalar_product(s_old, S_sum));

    // Implementing the Metropolis algorithm
    if (dE < 0) {
        lattice[i][j][k].sx = s_trial.sx;
        lattice[i][j][k].sy = s_trial.sy;
        acc = 1;
    } else {
        w = myrand();
        y = exp(-beta * dE);
        if (w <= y) {
            lattice[i][j][k].sx = s_trial.sx;
            lattice[i][j][k].sy = s_trial.sy;
            acc = 1;
        }
    }

    return acc;
}
