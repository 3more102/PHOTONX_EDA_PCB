#ifndef PHOTONX_NATIVE_H
#define PHOTONX_NATIVE_H

#include <stdint.h>

#if defined(_WIN32)
  #if defined(PHOTONX_NATIVE_BUILD)
    #define PHOTONX_NATIVE_API __declspec(dllexport)
  #else
    #define PHOTONX_NATIVE_API __declspec(dllimport)
  #endif
#else
  #define PHOTONX_NATIVE_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct photonx_aabb {
    double min_x;
    double min_y;
    double max_x;
    double max_y;
} photonx_aabb;

typedef struct photonx_pair {
    uint32_t first;
    uint32_t second;
} photonx_pair;

typedef struct photonx_point {
    double x;
    double y;
} photonx_point;

typedef struct photonx_neighbor {
    uint32_t query;
    uint32_t point;
    double distance;
} photonx_neighbor;

enum photonx_native_status {
    PHOTONX_NATIVE_OK = 0,
    PHOTONX_NATIVE_BUFFER_TOO_SMALL = 1,
    PHOTONX_NATIVE_INVALID_ARGUMENT = 2,
    PHOTONX_NATIVE_UNSUPPORTED_RANGE = 3,
    PHOTONX_NATIVE_INTERNAL_ERROR = 4
};

PHOTONX_NATIVE_API uint32_t photonx_native_abi_version(void);

PHOTONX_NATIVE_API int photonx_candidate_pairs(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double tolerance,
    double cell_size,
    photonx_pair* out_pairs,
    uint32_t out_capacity,
    uint32_t* out_count
);

PHOTONX_NATIVE_API int photonx_radius_neighbors(
    const photonx_point* points,
    uint32_t point_count,
    const photonx_point* queries,
    uint32_t query_count,
    double radius,
    double cell_size,
    photonx_neighbor* out_neighbors,
    uint32_t out_capacity,
    uint32_t* out_count
);

#ifdef __cplusplus
}
#endif

#endif
