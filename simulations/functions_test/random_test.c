#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "../include/random.h"

int main(void) {
    const unsigned long int seed1 = (unsigned long int) time(NULL); // seed for rng from current time
    const unsigned long int seed2 = seed1+127; // second seed for rng
    
    // initialize random number generator
    myrand_init(seed1, seed2); // function in random.h

    fprintf(stdout, "%lf\n", myrand());
}
