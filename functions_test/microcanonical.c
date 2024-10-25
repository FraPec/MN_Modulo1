#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "../include/functions.h"

int main(void) {
    DoubleVector2D * s, * S, * s_result;
    s = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));
    S = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));
    s_result = (DoubleVector2D *)malloc(sizeof(DoubleVector2D));

    s->sx = 1.5; s->sy = 2.3;
    S->sx = 0.0; S->sy = 124.2;
    s_result->sx = -s->sx; s_result->sy = s->sy;
    int i;

    fprintf(stdout, "FIRST TEST:\n");
    fprintf(stdout, "Starting vector s:\n");
    fprintf(stdout, "%lf, %lf\n", s->sx, s->sy);
    fprintf(stdout, "Vector S:\n");
    fprintf(stdout, "%lf, %lf\n", S->sx, S->sy);
    if (microcanonical(s, S) == EXIT_SUCCESS) {
        fprintf(stdout, "New vector s from function:\n");
        fprintf(stdout, "%lf, %lf\n", s->sx, s->sy);
	fprintf(stdout, "New vector s, real result:\n");
        fprintf(stdout, "%lf, %lf\n", s_result->sx, s_result->sy);
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
    }

    int is_equal = 0;
    if ((fabs(s->sx - s_result->sx)>1e-15) & fabs(s->sx - s_result->sx)>1e-15) { // NB: pay attetion to == with doubles!
        fprintf(stdout, "Error in first test!\n");
        is_equal = 2;
    }


    if (is_equal==0) { 
	fprintf(stdout, "First test passed, the results are equal!\n");
    } else {
        fprintf(stdout, "First test didn't work!\n");
    }
    fprintf(stdout, "\n");
   

    S->sx = 1e-14; S->sy = 1e-14;

    fprintf(stdout, "SECOND TEST:\n");
    fprintf(stdout, "Starting vector s:\n");
    fprintf(stdout, "%lf, %lf\n", s->sx, s->sy);
    fprintf(stdout, "Vector S:\n");
    fprintf(stdout, "%lf, %lf\n", S->sx, S->sy);

    if (microcanonical(s, S) == EXIT_SUCCESS) {
        fprintf(stdout, "Second test didn't work!\n");
    } else {
        fprintf(stderr, "Error in microcanonical function: norm of S is too small.\n");
        fprintf(stdout, "Second test passed, for |S| < 1e-13 it returned an error!\n");
    }
    
    
    return EXIT_SUCCESS;
}
