//
// Created by john on 1/24/20.
//

#include "keygen.h"

#include <string.h>

#define BLOCK_SIZE 16

const char alpha[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

void GenerateToken(int n, char *out) {
    int rseed = n;

    for (int i = 0; i < TOK_SIZE; i++) {
        rseed = (rseed * 17 + 42) % strlen(alpha);
        out[i] = alpha[rseed];
    }
}

int ValidateToken(int n, char *token) {
    char t[TOK_SIZE];
    GenerateToken(n, t);
    return strcmp(t, token) == 0;
}
