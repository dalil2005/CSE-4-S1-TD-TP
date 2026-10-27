#include <stdio.h>
#include <string.h>
#include <windows.h>
#include <cpuid.h>

static double now_s(void){
    LARGE_INTEGER f, c;
    QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&c);
    return (double)c.QuadPart / (double)f.QuadPart;
}

static void cpu_brand(char *out){
    unsigned r[12];
    __get_cpuid(0x80000002, &r[0], &r[1], &r[2],  &r[3]);
    __get_cpuid(0x80000003, &r[4], &r[5], &r[6],  &r[7]);
    __get_cpuid(0x80000004, &r[8], &r[9], &r[10], &r[11]);
    memcpy(out, r, 48);
    out[48] = 0;
}

int main(void){
    char brand[64];
    cpu_brand(brand);

    SYSTEM_INFO si;
    GetSystemInfo(&si);

    printf("CPU: %s\n", brand);
    printf("Logical threads: %lu\n", si.dwNumberOfProcessors);

    double t0 = now_s();
    volatile double s = 0.0;
    for (long i = 0; i < 200000000L; i++) s += 1.0;
    double t1 = now_s();

    printf("Simple loop (2e8 adds): %.3f s\n", t1 - t0);
    return 0;
}