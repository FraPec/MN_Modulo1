#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define DIM 3

int print_vector(double * x, int len_x) {
    int i;
    for (i=0; i<len_x; i++) {
        fprintf(stdout, "%lf ", x[i]);
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

int main(void) {
    double x[DIM], y[DIM];
    double scalar_prod;
    int i;

    for (i=0; i<DIM; i++) {
	x[i] = 1.0;
        y[i] = 2.0;
    }

    fprintf(stdout, "Scalar product between:");
    print_vector(x, DIM);
    print_vector(y, DIM);
    scalar_prod = scalar_product(x, y, DIM);
    fprintf(stdout, "scalar product = %lf\n", scalar_prod);

    return EXIT_SUCCESS;
}
