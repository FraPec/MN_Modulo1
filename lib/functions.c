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

double scalar_product(double * x, double * y, int dim) {
    int i;
    double scalar_prod = 0.0;
    for (i=0; i<dim; i++) {
        scalar_prod += x[i] * y[i];
    }
    return scalar_prod;
}

int microcanonical(double *s, double *S, int len_s) {
    double sq_mod_S, sS_scal_prod;
    int i;

    sq_mod_S = scalar_product(S, S, len_s);
    if (sqrt(sq_mod_S)<1e-13) {
        return EXIT_FAILURE;
    } else {
	sS_scal_prod = scalar_product(s, S, len_s);
	for (i=0; i<len_s; i++) {
	    s[i] = 2 * S[i] * sS_scal_prod / sq_mod_S - s[i];
	}
	return EXIT_SUCCESS;
    }
}

int normalization(double * r, int len_r) {
// How many normalizations needed during a simulation?

    int i;
    double mod_r = sqrt(scalar_product(r, r, len_r));

    for (i=0; i<len_r; i++) {
        r[i] = r[i] / mod_r;
    }

    mod_r = sqrt(scalar_product(r, r, len_r));
    if (fabs(mod_r-1.0)<1e-15) {
        return EXIT_SUCCESS;
    } else {
        fprintf(stderr, "Renormalization of vector failed!\n");
        return EXIT_FAILURE;
    }
}

void free_lattice(DoubleVector2D ***lattice, int lattice_side) {
    int i, j;
    for (i=0; i<lattice_side; i++) {
        for (j=0; j<lattice_side; j++) {
            free(lattice[i][j]);
        }
        free(lattice[i]);
    }
    free(lattice);
}

int allocate(DoubleVector2D ****lattice, int lattice_side) {
    int i, j, k, l;

    // First level allocation - array of pointers (2D lattice) to array of pointers (3D lattice) to 2dVector
    *lattice = (DoubleVector2D ***)malloc(lattice_side * sizeof(DoubleVector2D **));
    if (*lattice==NULL) {
        fprintf(stderr, "Error in the allocation of the first level.\n");
        return EXIT_FAILURE;
    }

    // Second level allocation - array of pointers (3D lattice) to 2dVector
    for (i=0; i<lattice_side; i++) {
        (*lattice)[i] = (DoubleVector2D **)malloc(lattice_side * sizeof(DoubleVector2D *));

        if ((*lattice)[i]==NULL) {
            fprintf(stderr, "Error in the allocation of the second level.\n");
            for (k=0; k<i; k++) {
                free((*lattice)[k]);
            }
            free(*lattice);
	return EXIT_FAILURE;
        }

        // Third level allocation - pointers to 2dVector
        for (j=0; j<lattice_side; j++) {
            (*lattice)[i][j] = (DoubleVector2D *)malloc(lattice_side * sizeof(DoubleVector2D));
            if ((*lattice)[i][j]==NULL) {

                fprintf(stderr, "Error in the allocation of the second level.\n");

                // Deallocation of j pointers to 2dVector along the (2D) lattice site identified by i
                for (l=0; l<j; l++) {
                        free((*lattice)[i][l]);
                    }
                free((*lattice)[i]);

                // Deallocation of (i x lattice_side) pointers to 2dVector
                for (k=0; k<i; k++) {
                    for (l=0; l<lattice_side; l++) {
                        free((*lattice)[k][l]);
                    }
                    free((*lattice)[k]);

                }
                free(*lattice);
                return EXIT_FAILURE;
            }
        }
    }
    return EXIT_SUCCESS;
}
