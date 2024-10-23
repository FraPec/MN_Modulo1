#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define L 5

// Vector structure 
typedef struct DoubleVector2D {
    double sx;
    double sy;
} DoubleVector2D;


void free_lattice(DoubleVector2D ***lattice, int lattice_side) {
    int i, j;
    for (i=0; i<lattice_side; i++) {
        for (j=0; j<lattice_side; j++) {
            free(lattice[i][j]);
        }
        free(lattice[i]);
    }
    free(lattice);
}


int allocate(DoubleVector2D ****lattice, int lattice_side) {
    int i, j, k, l;
    
    // First level allocation - array of pointers (2D lattice) to array of pointers (3D lattice) to 2dVector
    *lattice = (DoubleVector2D ***)malloc(lattice_side * sizeof(DoubleVector2D **)); 
    if (*lattice==NULL) {
        fprintf(stderr, "Error in the allocation of the first level.\n");
        return EXIT_FAILURE;
    }

    // Second level allocation - array of pointers (3D lattice) to 2dVector
    for (i=0; i<lattice_side; i++) {
        (*lattice)[i] = (DoubleVector2D **)malloc(lattice_side * sizeof(DoubleVector2D *));

        if ((*lattice)[i]==NULL) {
            fprintf(stderr, "Error in the allocation of the second level.\n");
            for (k=0; k<i; k++) {
                free((*lattice)[k]);
            }
            free(*lattice);
	return EXIT_FAILURE;
        }
        
        // Third level allocation - pointers to 2dVector
        for (j=0; j<lattice_side; j++) {
            (*lattice)[i][j] = (DoubleVector2D *)malloc(lattice_side * sizeof(DoubleVector2D));
            if ((*lattice)[i][j]==NULL) {
            
                fprintf(stderr, "Error in the allocation of the second level.\n");
                
                // Deallocation of j pointers to 2dVector along the (2D) lattice site identified by i
                for (l=0; l<j; l++) {
                        free((*lattice)[i][l]);
                    }
                free((*lattice)[i]);         
                
                // Deallocation of (i x lattice_side) pointers to 2dVector
                for (k=0; k<i; k++) {
                    for (l=0; l<lattice_side; l++) {
                        free((*lattice)[k][l]);
                    }
                    free((*lattice)[k]);
                   
                }
                free(*lattice);
                return EXIT_FAILURE;
            }
        }
    }
    return EXIT_SUCCESS;
}


int main() {
    DoubleVector2D ***lattice;

    // Allocation and check if all went well
    if (allocate(&lattice, L) == EXIT_FAILURE) {
        return EXIT_FAILURE;
    }

    // Setting all value
    lattice[0][0][0].sx = 1.0;
    lattice[0][0][0].sy = 2.0;

    printf("Value of lattice[0][0][0]: sx = %.2f, sy = %.2f\n", lattice[0][0][0].sx, lattice[0][0][0].sy);

    // Free the lattice
    free_lattice(lattice, L);

    return EXIT_SUCCESS;
}

