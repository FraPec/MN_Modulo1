#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"


#define L 5 // Define the size of the lattice





int main() {
    DoubleVector2D ***lattice;
    double a = 1.0;
    int i, j, k;

    // Allocate the lattice and check if allocation was successful
    lattice = allocate(L);
    if (lattice == NULL) {
        fprintf(stderr, "Error: Allocation of lattice failed.\n");
        return EXIT_FAILURE;
    }

    // Initialize values in the dynamically allocated lattice
    for (i = 0; i < L; i++) {
        for (j = 0; j < L; j++) {
            for (k = 0; k < L; k++) {
                lattice[i][j][k].sx = a;  // Set sx to 1.0
                lattice[i][j][k].sy = a;  // Set sy to 1.0
            }
        }
    }

    // Test: Verify that each element in lattice has sx = 1.0 and sy = 1.0
    int flag = 0;  // Flag to track if any element is incorrect
    for (i = 0; i < L; i++) {
        for (j = 0; j < L; j++) {
            for (k = 0; k < L; k++) {
                // Check if either sx or sy does not match the expected value
                if (lattice[i][j][k].sx != a || lattice[i][j][k].sy != a) {
                    flag = 1;  // Set flag if there's a mismatch
                    break;
                }
            }
            if (flag == 1) {
                break;
            }
        }
        if (flag == 1) {
            break;
        }
    }

    // Output result of the test
    if (flag == 0) {
        printf("Test passed! All elements in lattice initialized correctly.\n");
    } else {
        printf("Test failed: Some elements in lattice do not match the expected values.\n");
    }

    // Free the lattice
    free_lattice(lattice, L);

    return EXIT_SUCCESS;
}
