#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "../include/functions.h"

int main() {
    DoubleVector2D * s;
    s = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));
    s->sx = 123.4; s->sy = 1089.52;
    int i, normalized;
    double mod_s;

    fprintf(stdout, "Vector before normalization:\n");
    fprintf(stdout, "%lf, %lf\n", s->sx, s->sy);

    mod_s = scalar_product(*s, *s);
    mod_s = sqrt(mod_s);

    fprintf(stdout, "Modulus of vector before normalization: %lf\n", mod_s);

    normalized = normalization(s);
    mod_s = scalar_product(*s, *s);
    mod_s = sqrt(mod_s);

    fprintf(stdout, "Vector after normalization:\n");
    fprintf(stdout, "%lf, %lf\n", s->sx, s->sy);
    fprintf(stdout, "Modulus of vector after normalization: %lf\n", mod_s);
    
    if (normalized==EXIT_SUCCESS) {
        fprintf(stdout, "Test passed, vector has been correctly normalized!\n");
    } else {
        fprintf(stderr, "Test didn't work, something went wrong with the normalization\n");
    }

    return EXIT_SUCCESS;
}
