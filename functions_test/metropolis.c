#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "../include/functions.h"
#include "../include/random.h"

int local_metropolis(DoubleVector2D ****lattice, int i, int j, int k, int lattice_side, double alpha, double beta) {
    int i_minus, i_plus, j_minus, j_plus, k_minus, k_plus;
    double t, theta, dE, w, y;
    DoubleVector2D s_old, s_trial, S_sum;

    // Controllo della validità degli indici
    if (i < 0 || i >= lattice_side || j < 0 || j >= lattice_side || k < 0 || k >= lattice_side) {
        fprintf(stderr, "Invalid lattice indices: %d, %d, %d. Lattice side is %d \n", i, j, k, lattice_side);
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
    S_sum.sx = lattice[i_minus][j][k]->sx + lattice[i_plus][j][k]->sx +
               lattice[i][j_minus][k]->sx + lattice[i][j_plus][k]->sx +
               lattice[i][j][k_minus]->sx + lattice[i][j][k_plus]->sx;

    S_sum.sy = lattice[i_minus][j][k]->sy + lattice[i_plus][j][k]->sy +
               lattice[i][j_minus][k]->sy + lattice[i][j_plus][k]->sy +
               lattice[i][j][k_minus]->sy + lattice[i][j][k_plus]->sy;

    // Calcolo di dE (energia) tra la configurazione di prova e quella vecchia
    dE = -(scalar_product(s_trial, S_sum) - scalar_product(s_old, S_sum));

    // Implementazione dell'algoritmo di Metropolis
    if (dE < 0) {
        lattice[i][j][k]->sx = s_trial.sx;
        lattice[i][j][k]->sy = s_trial.sy;
    } else {
        w = myrand();
        y = exp(-beta * dE);
        if (w <= y) {
            lattice[i][j][k]->sx = s_trial.sx;
            lattice[i][j][k]->sy = s_trial.sy;
        }
    }

    return EXIT_SUCCESS;
}




// Inizializza tutti i valori della matrice con sx = 1 e sy = 0
void initialize_lattice(DoubleVector2D ***lattice, int lattice_side) {
    for (int i = 0; i < lattice_side; i++) {
        for (int j = 0; j < lattice_side; j++) {
            for (int k = 0; k < lattice_side; k++) {
                lattice[i][j][k].sx = 1.0;
                lattice[i][j][k].sy = 0.0;
            }
        }
    }
}



int main() {
    int lattice_side = 5;   // Dimensione della matrice 3D
    double alpha = 0.1;     // Parametro per calcolare theta
    double beta = 0.5;      // Parametro per Metropolis

    // Dichiarazione della matrice lattice
    DoubleVector2D ***lattice;

    // Allocazione della matrice e controllo errori
    if (allocate(&lattice, lattice_side) == EXIT_FAILURE) {
        fprintf(stderr, "Errore nell'allocazione della matrice.\n");
        return EXIT_FAILURE;
    }

    // Inizializzazione della matrice con sx = 1 e sy = 0
    initialize_lattice(lattice, lattice_side);

    // Test della funzione local_metropolis su un sito specifico
    int i = 2, j = 2, k = 2;  // Indici del sito da aggiornare
    int result = local_metropolis(&lattice, i, j, k, lattice_side, alpha, beta);

    // Verifica del risultato
    if (result == EXIT_SUCCESS) {
        printf("Aggiornamento riuscito per lattice[%d][%d][%d]: sx = %.3f, sy = %.3f\n",
               i, j, k, lattice[i][j][k].sx, lattice[i][j][k].sy);
    } else {
        fprintf(stderr, "Errore durante l'aggiornamento di lattice[%d][%d][%d]\n", i, j, k);
    }

    // Liberazione della memoria
    free_lattice(lattice, lattice_side);

    return EXIT_SUCCESS;
}
