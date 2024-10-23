#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"
#include "../include/random.h"


int local_metropolis(DoubleVector2D ****lattice, int i, int j, int k, int lattice_side, double alpha) {

    int i_minus, i_plus, j_minus, j_plus, k_minus, k_plus;
    double t, theta;
    DoubleVector2D s_old, s_trial, s_sum;

    // Controllo della validità degli indici
    if (i < 0 || i >= lattice_side || j < 0 || j >= lattice_side || k < 0 || k >= lattice_side) {
        fprintf(stderr, "Invalid lattice indeces: %d, %d, %d. Lattice side is %d \n", i, j, k, lattice_side);
        return EXIT_FAILURE;
    }

    // Calcolo degli indici dei vicini con condizioni di bordo periodiche
    i_minus = (i - 1 + lattice_side) % lattice_side;
    i_plus  = (i + 1) % lattice_side;
    j_minus = (j - 1 + lattice_side) % lattice_side;
    j_plus  = (j + 1) % lattice_side;
    k_minus = (k - 1 + lattice_side) % lattice_side;
    k_plus  = (k + 1) % lattice_side;

    // Generazione del numero casuale U([0,1)) e calcolo di theta
    t = myrand();
    theta = (2 * t - 1) * alpha;

    // Ottenere i valori correnti per lo spin nel sito
    s_old = *lattice[i][j][k];

    // Generare lo stato di prova (trial state) partendo da quello vecchio
    s_trial.sx = cos(theta) * s_old.sx + sin(theta) * s_old.sy;
    s_trial.sy = -sin(theta) * s_old.sx + cos(theta) * s_old.sy;

    // Calcolare la somma dei vicini per sx e sy
    s_sum.sx = lattice[i_minus][j][k]->sx + lattice[i_plus][j][k]->sx +
               lattice[i][j_minus][k]->sx + lattice[i][j_plus][k]->sx +
               lattice[i][j][k_minus]->sx + lattice[i][j][k_plus]->sx;

    s_sum.sy = lattice[i_minus][j][k]->sy + lattice[i_plus][j][k]->sy +
               lattice[i][j_minus][k]->sy + lattice[i][j_plus][k]->sy +
               lattice[i][j][k_minus]->sy + lattice[i][j][k_plus]->sy;

    // Resto della logica (ad esempio accettazione o rifiuto dello stato trial)
    // ...

    return EXIT_SUCCESS;
}
