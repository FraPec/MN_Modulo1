#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"


#define L 5



int main() {
    DoubleVector2D ***lattice;
    double a = 1.0;
    int i, j, k;

    // Allocation and check if all went well
    if (allocate(&lattice, L) == EXIT_FAILURE) {
        fprintf(stderr, "male male male/n");
        return EXIT_FAILURE;
    }

    // Setting values in the dynamically allocated lattice
    for (i=0; i<L; i++) {
        for (j=0; j<L; j++) {
            for (k=0; k<L; k++) {
                lattice[i][j][k].sx = a;
                lattice[i][j][k].sy = a;
            }
        }
    }

    // test
    int flag = 0;
    for (i=0; i<L; i++) {
        for (j=0; j<L; j++) {
            for (k=0; k<L; k++) {
                if (lattice[i][j][k].sx != a & lattice[i][j][k].sy != a ) {
                flag = 1;
                }
                if (flag == 1) {
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

    if (flag == 0) { // Free the lattice
      free_lattice(lattice, L);
      printf("Test passed! Great job\n");
    } else {
        printf("Test failed\n");
    }

    return EXIT_SUCCESS;
}
