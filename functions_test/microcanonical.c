#include <stdio.h>
#include <stdlib.h>

#include "../include/functions.h"

#define DIM 2

int main(void) {
    double s[DIM] = {2.0, 3.0}, S[DIM] = {0.0, 3.0};

    fprintf(stdout, "Starting vector s:\n");
    print_vector(s, DIM);
    fprintf(stdout, "Vector S:\n");
    print_vector(S, DIM);
    if (microcanonical(s, S, DIM) == EXIT_SUCCESS) {
        fprintf(stdout, "New vector s:\n");
        print_vector(s, DIM);
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
    }

    return EXIT_SUCCESS;
}
