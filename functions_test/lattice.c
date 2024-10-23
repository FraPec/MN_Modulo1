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


    double a = 1.0;
    int i, j, k;



    // Allocation and check if all went well
    if (allocate(&lattice, L) == EXIT_FAILURE) {
        fprintf(stderr, "male male male/n");
        return EXIT_FAILURE;
    }


    // Setting values in the dynamically allocated lattice
    for (i=0; i<L; i++){
      for (j=0; j<L; j++){
        for (k=0; k<L; k++){
         lattice[i][j][k].sx = a;
         lattice[i][j][k].sy = a;
      }
     }
    }


    // test
    int flag = 0;

    for (i=0; i<L; i++){

      for (j=0; j<L; j++){

        for (k=0; k<L; k++){

         if (lattice[i][j][k].sx != a & lattice[i][j][k].sy != a ){
           flag = 1;
         }

         if (flag == 1) {
           break;
         }

      }
      if (flag == 1) {
        break;
      }

     }
     if (flag == 1){
       break;
     }

    }


    if (flag == 0)
    { // Free the lattice
      free_lattice(lattice, L);
      printf("Test passed! Great job\n");
    }
    else {
      printf("Test failed\n");
    }


    return EXIT_SUCCESS;
}
