#ifndef FUNCTIONS
#define FUNCTIONS

typedef struct {
    double sx;
    double sy;
} DoubleVector2D;

double scalar_product(DoubleVector2D s1, DoubleVector2D s2);
int microcanonical(DoubleVector2D *s, DoubleVector2D *S);
int normalization(DoubleVector2D *s);
void free_lattice(DoubleVector2D ***lattice, int lattice_side);
DoubleVector2D ***allocate(int lattice_side);
DoubleVector2D* magnetization(DoubleVector2D ***lattice, int lattice_side);
double energy_per_site(DoubleVector2D ***lattice, int lattice_side);

#endif
