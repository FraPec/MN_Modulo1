#include <stdio.h>
#include <math.h>
#include <stdlib.h>

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
    if (pow(sq_mod_S, 0.5)<1e-13) { 
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
    int i;
    double mod_r = pow(scalar_product(r, r, len_r), 0.5);

    for (i=0; i<len_r; i++) {
        r[i] = r[i] / mod_r;
    }

    mod_r = pow(scalar_product(r, r, len_r), 0.5);
    if (fabs(mod_r-1)<1e-15) {
        return EXIT_SUCCESS;
    } else {
        fprintf(stderr, "Renormalization of vector failed!\n");
        return EXIT_FAILURE;
    }
}

