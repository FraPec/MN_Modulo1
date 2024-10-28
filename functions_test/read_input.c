#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/functions.h"

#define MAX_LENGTH 128

int main(int argc, char *argv[]) {

    if (argc != 2) {
        fprintf(stdout, "Invalid number of parameters!\nHow to use this program:\n");
	fprintf(stdout, "./program input_file\n");
	return EXIT_SUCCESS;
    }

    char file_name[MAX_LENGTH];
    strcpy(file_name, argv[1]);
    fprintf(stdout, "File name: %s\n", file_name);
    
    FILE *file = fopen(file_name, "r");
    if (file == NULL) {
        fprintf(stderr, "Error opening file\n");
        return EXIT_SUCCESS;
    }

    char param_name1[50] = "beta";
    char param_type1[50] = "%d";
    int param_value1;

    char param_name2[50] = "alpha";
    char param_type2[50] = "%d";
    int param_value2;

    
    int param_found = 0;
    param_found = read_parameter(file, param_name1, param_type1, &param_value1);
    fprintf(stdout,"First test:\n");
    if (param_found==1) {
        fprintf(stdout, "Parameter found, %s = %d.\nTest passed!\n\n", param_name1, param_value1);
    } else {
        fprintf(stdout, "Parameter not found.\nTest failed!\n\n");
    }

    param_found = 0;
    param_found = read_parameter(file, param_name2, param_type2, &param_value2);
    fprintf(stdout,"Second test:\n");
    if (param_found==0) {
        fprintf(stdout, "Parameter not found.\nTest passed!\n");
    } else {
        fprintf(stdout, "Test failed!\n");
    }

    fclose(file);
    
    return EXIT_SUCCESS;    
}
