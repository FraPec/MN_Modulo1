#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"



int main(){

    DoubleVector2D v1, v2;

    v1.sx = 1.0;
    v1.sy = 2.0;
    v2.sx = 7.0;
    v2.sy = 3.0;

    double scal_p = scalar_product(v1, v2);

    printf("Result: %lf\n", scal_p);


    return EXIT_SUCCESS;
}
