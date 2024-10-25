#ifndef FUNCTIONS
#define FUNCTIONS

typedef struct {
    double sx;
    double sy;
} DoubleVector2D;

int print_vector(double * x, int len_x);
double scalar_product(DoubleVector2D s1, DoubleVector2D s2);
int microcanonical(double *s, double *S, int len_s);
int normalization(double * r, int len_r);
void free_lattice(DoubleVector2D ***lattice, int lattice_side);
DoubleVector2D ***allocate(int lattice_side);

#endif
