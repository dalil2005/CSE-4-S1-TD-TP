#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <windows.h>
#include <malloc.h>

static double now_s(void){
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart / (double)f.QuadPart;
}

#define REPS 3

int main(int argc, char **argv){
    size_t N = (argc > 1) ? (size_t)atof(argv[1]) : 100000000;
    N = (N / 16) * 16;

    float *A = (float*)_aligned_malloc(N * sizeof(float), 64);
    float *B = (float*)_aligned_malloc(N * sizeof(float), 64);
    float *C = (float*)_aligned_malloc(N * sizeof(float), 64);
    if (!A || !B || !C){ fprintf(stderr, "alloc failed\n"); return 1; }

    for (size_t i = 0; i < N; i++){ A[i] = 1.0f; B[i] = 2.0f; C[i] = 0.0f; }

    double best = 1e30, sum = 0.0;
    for (int r = 0; r < REPS; r++){
        double t0 = now_s();
        for (size_t i = 0; i < N; i++) C[i] = A[i] + B[i];
        double t1 = now_s();
        double dt = t1 - t0;
        if (dt < best) best = dt;
        sum += dt;
        A[r] += 0.0f;
    }
    double avg = sum / REPS;

    int ok = 1;
    for (size_t i = 0; i < N; i += N / 10) if (C[i] != 3.0f) ok = 0;
    printf("C[0]=%.1f C[N/2]=%.1f C[N-1]=%.1f -> %s\n",
           C[0], C[N/2], C[N-1], ok ? "OK" : "WRONG");

    double bytes = 3.0 * (double)N * sizeof(float);
    printf("N=%zu  best=%.4f s  avg=%.4f s\n", N, best, avg);
    printf("Throughput best: %.2f GB/s | avg: %.2f GB/s\n",
           bytes / best / 1e9, bytes / avg / 1e9);
    printf("Adds best: %.3f GFLOP/s\n", (double)N / best / 1e9);

    _aligned_free(A); _aligned_free(B); _aligned_free(C);
    return 0;
}