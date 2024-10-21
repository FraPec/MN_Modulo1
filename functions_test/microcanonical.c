#include <stdio.h>
#include <stdlib.h>

#include "../include/functions.h"

#define DIM 2

int main(void) {
    double s[DIM] = {12.9, 3.5}, S[DIM] = {0.0, 127.97}, s_result[DIM];
    int i;
    for (i=0; i<DIM; i++) {
        s_result[i] = s[i];
    }
    s_result[0] = - s_result[0];

    fprintf(stdout, "FIRST TEST:\n");
    fprintf(stdout, "Starting vector s:\n");
    print_vector(s, DIM);
    fprintf(stdout, "Vector S:\n");
    print_vector(S, DIM);
    if (microcanonical(s, S, DIM) == EXIT_SUCCESS) {
        fprintf(stdout, "New vector s from function:\n");
        print_vector(s, DIM);
	fprintf(stdout, "New vector s, real result:\n");
	print_vector(s_result, DIM);
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
    }
    int is_equal = 0;
    for (i=0; i<DIM; i++) {
    	if (abs(s[i] - s_result[i])>1e-15) { // NB: pay attetion to == with doubles!
	    fprintf(stdout, "Error in first test!\n");
	    is_equal = 2;
	    break;
	}
    }
    if (is_equal==0) { 
	fprintf(stdout, "First test passed, the results are equal!\n");
    } else {
        fprintf(stdout, "First test didn't work!\n");
    }
    fprintf(stdout, "\n");
    

    for (i=0; i<DIM; i++) {
        S[i] = 1e-14; 
    }    
    fprintf(stdout, "SECOND TEST:\n");
    fprintf(stdout, "Starting vector s:\n");
    print_vector(s, DIM);
    fprintf(stdout, "Vector S:\n");
    print_vector(S, DIM);
    if (microcanonical(s, S, DIM) == EXIT_SUCCESS) {
        fprintf(stdout, "Second test didn't work!\n");
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
        fprintf(stdout, "Second test passed, for |S| < 1e-13 it returned an error!\n");
    }
    
    
    return EXIT_SUCCESS;
}
