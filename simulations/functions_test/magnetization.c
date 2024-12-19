#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"


#define L 5

int main() {
    DoubleVector2D ***lattice = allocate(L);
    double a = 127.32, b = 134.123;
    int i, j, k;

    // Allocate lattice
    if (lattice == NULL) {
        return EXIT_FAILURE;
    }

    // Setting values in the dynamically allocated lattice
    for (i=0; i<L; i++) {
        for (j=0; j<L; j++) {
            for (k=0; k<L; k++) {
                lattice[i][j][k].sx = a;
                lattice[i][j][k].sy = b;
            }
        }
    }
    
    DoubleVector2D * m = magnetization(lattice, L);
    
    if (m==NULL) {
	fprintf(stderr, "Test failed due to allocation issues!\n");
        return EXIT_FAILURE;
    } 

    if ((fabs(m->sx-a)<1e-12)&&(fabs(m->sy-b)<1e-12)) {
        fprintf(stdout, "Test passed, vector magnetization is equal to the right value!\n");
	fprintf(stdout, "m = (%.15lf, %.15lf), correct value = (%.15lf, %.15lf)\n", m->sx, m->sy, a, b);
        return EXIT_SUCCESS;
    } else {
        fprintf(stdout, "Test failed, vector magnetization is NOT equal to the right value!\n");
        fprintf(stdout, "m = (%.15lf, %.15lf), correct value = (%.15lf, %.15lf)\n", m->sx, m->sy, a, b);
	return EXIT_SUCCESS;
    }

}

