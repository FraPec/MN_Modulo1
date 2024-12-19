#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "../include/functions.h"
#define L 5

int main(void) {
    DoubleVector2D ***lattice, * s_result;
    s_result = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));
    // Allocate the lattice and check if allocation was successful
    lattice = allocate(L);
    if (lattice == NULL) {
        fprintf(stderr, "Error: Allocation of lattice failed.\n");
        return EXIT_FAILURE;
    }
    // Initialize all the lattice 
    int i, j, k;
    double a = 12.4, b = 0.0;
    for (i=0; i<L; i++) {
        for (j=0; j<L; j++) {
            for (k=0; k<L; k++) {
                lattice[i][j][k].sx = a;
                lattice[i][j][k].sy = b;
            }
        }
    }   

    lattice[0][1][L-1].sx = 1.5; lattice[0][1][L-1].sy = 124.3;
    s_result->sx = lattice[0][1][L-1].sx; s_result->sy = -lattice[0][1][L-1].sy;

    fprintf(stdout, "FIRST TEST:\n");
    fprintf(stdout, "Starting vector s:\n");
    fprintf(stdout, "%.14lf, %.14lf\n", lattice[0][1][L-1].sx, lattice[0][1][L-1].sy);
    fprintf(stdout, "Vector S:\n");
    fprintf(stdout, "%.14lf, %.14lf\n", 4*a, 4*b);
    if (microcanonical(lattice, 0, 1, L-1, L) == 1) {
        fprintf(stdout, "New vector s from function:\n");
        fprintf(stdout, "%.14lf, %.14lf\n", lattice[0][1][L-1].sx, lattice[0][1][L-1].sy);
	fprintf(stdout, "New vector s, real result:\n");
        fprintf(stdout, "%.14lf, %.14lf\n", s_result->sx, s_result->sy);
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
    }

    int is_equal = 0;
    if ((fabs(lattice[0][1][L-1].sx - s_result->sx)>1e-15) & fabs(lattice[0][1][L-1].sy - s_result->sy)>1e-15) { // NB: pay attetion to == with doubles!
        fprintf(stdout, "Error in first test!\n");
        is_equal = 2;
    }


    if (is_equal==0) { 
	fprintf(stdout, "First test passed, the results are equal!\n");
    } else {
        fprintf(stdout, "First test didn't work!\n");
    }
    fprintf(stdout, "\n");
   

    a = 1e-14, b = 1e-14;
    for (i=0; i<L; i++) {
        for (j=0; j<L; j++) {
            for (k=0; k<L; k++) {
                lattice[i][j][k].sx = a;
                lattice[i][j][k].sy = b;
            }
        }
    } 
    lattice[0][1][L-1].sx = 1.5; lattice[0][1][L-1].sy = 124.3;


    fprintf(stdout, "SECOND TEST:\n");
    fprintf(stdout, "Starting vector s:\n");
    fprintf(stdout, "%.14lf, %.14lf\n", lattice[0][1][L-1].sx, lattice[0][1][L-1].sy);
    fprintf(stdout, "Vector S:\n");
    fprintf(stdout, "%.14lf, %.14lf\n", 4*a, 4*b);

    if (microcanonical(lattice, 0, 1, L-1, L) == 1) {
        fprintf(stdout, "Second test didn't work!\n");
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
        fprintf(stdout, "Second test passed, for |S| < 1e-13 it returned an error!\n");
    }
    
    
    return EXIT_SUCCESS;
}
