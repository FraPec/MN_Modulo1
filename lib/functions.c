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
