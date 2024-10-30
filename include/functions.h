#ifndef FUNCTIONS
#define FUNCTIONS

#define PI 3.141592653589793

typedef struct {
    double sx;
    double sy;
} DoubleVector2D;

double scalar_product(DoubleVector2D s1, DoubleVector2D s2);
int normalization(DoubleVector2D *s);
void free_lattice(DoubleVector2D ***lattice, int lattice_side);
DoubleVector2D ***allocate(int lattice_side);
DoubleVector2D* magnetization(DoubleVector2D ***lattice, int lattice_side);
double energy_per_site(DoubleVector2D ***lattice, int lattice_side);
int initialize_lattice(DoubleVector2D ***lattice, int lattice_side);
int microcanonical(DoubleVector2D ***lattice, int i, int j, int k, int lattice_side);
int local_metropolis(DoubleVector2D ***lattice, int i, int j, int k, int lattice_side, double alpha, double beta);
int read_parameter(FILE *fp, char *param_name, char *param_type, void *value);

#endif
