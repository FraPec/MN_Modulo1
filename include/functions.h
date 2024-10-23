#ifndef FUNCTIONS
#define FUNCTIONS


typedef struct {
    double sx;
    double sy;
} DoubleVector2D;


int print_vector(double * x, int len_x);
double scalar_product(double * x, double * y, int dim);
int microcanonical(double *s, double *S, int len_s);
int normalization(double * r, int len_r);
void free_lattice(DoubleVector2D ***lattice, int lattice_side);
int allocate(DoubleVector2D ****lattice, int lattice_side);

#endif
