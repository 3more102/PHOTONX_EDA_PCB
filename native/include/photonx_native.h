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

typedef struct photonx_point_query {
    double x;
    double y;
    double radius;
} photonx_point_query;

typedef struct photonx_query_match {
    uint32_t query;
    uint32_t point;
} photonx_query_match;

typedef struct photonx_point_index photonx_point_index;

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

PHOTONX_NATIVE_API int photonx_point_index_create(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double cell_size,
    photonx_point_index** out_index
);

PHOTONX_NATIVE_API void photonx_point_index_destroy(
    photonx_point_index* index
);

PHOTONX_NATIVE_API int photonx_point_index_radius_candidates(
    const photonx_point_index* index,
    const photonx_point_query* queries,
    uint32_t query_count,
    photonx_query_match* out_matches,
    uint32_t out_capacity,
    uint32_t* out_count
);

PHOTONX_NATIVE_API int photonx_point_radius_candidates(
    const photonx_aabb* boxes,
    uint32_t box_count,
    const photonx_point_query* queries,
    uint32_t query_count,
    double cell_size,
    photonx_query_match* out_matches,
    uint32_t out_capacity,
    uint32_t* out_count
);

#ifdef __cplusplus
}
#endif

#endif
