#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"

#define DIM 3

int main(void) {
    double x[DIM], y[DIM];
    double scalar_prod_f, scalar_prod_result = 0;
    int i;

    for (i=0; i<DIM; i++) {
	x[i] = 1.0;
        y[i] = 2.0;
	scalar_prod_result += x[i]*y[i];
    }

    fprintf(stdout, "Scalar product between:\n");
    print_vector(x, DIM);
    print_vector(y, DIM);
    scalar_prod_f = scalar_product(x, y, DIM);
    fprintf(stdout, "Scalar product from function = %lf\n", scalar_prod_f);
    fprintf(stdout, "Real result: %lf\n", scalar_prod_result);
    return EXIT_SUCCESS;
}
