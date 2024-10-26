#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"


#define L 5

DoubleVector2D* magnetization(DoubleVector2D ***lattice, int lattice_side) {
    DoubleVector2D* m = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));
    int Vol = lattice_side * lattice_side * lattice_side; // faster and more accurate than pow (math.h) for integers!
    if (m==NULL) {
        fprintf(stderr, "Failed allocation for vector magnetization, returning NULL!\n");
	return NULL;
    }
    m->sx = 0.0; m->sy = 0.0;
    int i, j, k;
    
    for (i=0; i<lattice_side; i++) {
        for (j=0; j<lattice_side; j++) {
            for (k=0; k<lattice_side; k++) {
                m->sx += lattice[i][j][k].sx;
                m->sy += lattice[i][j][k].sy;
            }
        }
    }

    m->sx /= Vol;
    m->sy /= Vol;
    
    return m;
}


int main() {
    DoubleVector2D ***lattice;
    double a = 127.32, b = 134.123;
    int i, j, k;

    // Allocate lattice
    if (allocate(&lattice, L) == EXIT_FAILURE) {
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

