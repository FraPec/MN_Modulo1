#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "../include/functions.h"

#define DIM 5

int main() {
    double r[DIM] = {1.2, 1.3, 12.5, 4.4, 0.03}, mod_r = 0.0;
    int i, normalized;
    fprintf(stdout, "Vector before normalization:\n");
    print_vector(r, DIM);
    
    mod_r = scalar_product(r, r, DIM);
    mod_r = pow(mod_r, 0.5);
    fprintf(stdout, "Modulus of vector before normalization: %lf\n", mod_r);

    normalized = normalization(r, DIM);
    mod_r = scalar_product(r, r, DIM);
    mod_r = pow(mod_r, 0.5);
    fprintf(stdout, "Vector after normalization:\n");
    print_vector(r, DIM);

    fprintf(stdout, "Modulus of vector after normalization: %lf\n", mod_r);
    if (normalized==EXIT_SUCCESS) {
        fprintf(stdout, "Test passed, vector has been correctly normalized!\n");
    } else {
        fprintf(stderr, "Test didn't work, something went wrong with the normalization\n");
    }

    return EXIT_SUCCESS;
}
