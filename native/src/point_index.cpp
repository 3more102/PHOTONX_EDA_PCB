#include "photonx_native.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <memory>
#include <unordered_map>
#include <vector>

namespace {

constexpr long double kMaxCellsPerQuery = 1000000.0L;

struct Cell {
    int64_t x;
    int64_t y;

    bool operator==(const Cell& other) const noexcept {
        return x == other.x && y == other.y;
    }
};

struct CellHash {
    std::size_t operator()(const Cell& cell) const noexcept {
        const auto h1 = std::hash<int64_t>{}(cell.x);
        const auto h2 = std::hash<int64_t>{}(cell.y);
        return h1 ^ (h2 + static_cast<std::size_t>(0x9e3779b97f4a7c15ULL) +
                     (h1 << 6U) + (h1 >> 2U));
    }
};

using PointGrid = std::unordered_map<Cell, std::vector<uint32_t>, CellHash>;

bool finite_box(const photonx_aabb& box) noexcept {
    return std::isfinite(box.min_x) && std::isfinite(box.min_y) &&
           std::isfinite(box.max_x) && std::isfinite(box.max_y) &&
           box.min_x <= box.max_x && box.min_y <= box.max_y;
}

bool box_center(
    const photonx_aabb& box,
    double& center_x,
    double& center_y
) noexcept {
    if (!finite_box(box)) {
        return false;
    }

    // Deliberately mirror Python binary64 arithmetic.
    center_x = (box.min_x + box.max_x) / 2.0;
    center_y = (box.min_y + box.max_y) / 2.0;
    return std::isfinite(center_x) && std::isfinite(center_y);
}

bool to_cell(double coordinate, double cell_size, int64_t& out) noexcept {
    const double scaled = std::floor(coordinate / cell_size);
    const long double scaled_ld = static_cast<long double>(scaled);
    const long double lo =
        static_cast<long double>(std::numeric_limits<int64_t>::min());
    const long double hi =
        static_cast<long double>(std::numeric_limits<int64_t>::max());

    if (!std::isfinite(scaled) || scaled_ld < lo || scaled_ld > hi) {
        return false;
    }

    out = static_cast<int64_t>(scaled);
    return true;
}

bool query_cell_bounds(
    const photonx_aabb& box,
    double cell_size,
    int64_t& min_x,
    int64_t& min_y,
    int64_t& max_x,
    int64_t& max_y
) noexcept {
    if (!to_cell(box.min_x, cell_size, min_x) ||
        !to_cell(box.min_y, cell_size, min_y) ||
        !to_cell(box.max_x, cell_size, max_x) ||
        !to_cell(box.max_y, cell_size, max_y)) {
        return false;
    }

    const long double width =
        static_cast<long double>(max_x) - static_cast<long double>(min_x) + 1.0L;
    const long double height =
        static_cast<long double>(max_y) - static_cast<long double>(min_y) + 1.0L;
    if (width <= 0.0L || height <= 0.0L) {
        return false;
    }

    const long double cells = width * height;
    return std::isfinite(cells) && cells <= kMaxCellsPerQuery;
}

}  // namespace

struct photonx_point_index {
    double cell_size = 1.0;
    PointGrid grid;
    std::vector<double> center_x;
    std::vector<double> center_y;
};

extern "C" int photonx_point_index_create(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double cell_size,
    photonx_point_index** out_index
) {
    if (out_index == nullptr ||
        (box_count != 0U && boxes == nullptr) ||
        !std::isfinite(cell_size) || cell_size <= 0.0) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }

    *out_index = nullptr;

    try {
        auto index = std::make_unique<photonx_point_index>();
        index->cell_size = cell_size;
        index->center_x.assign(box_count, 0.0);
        index->center_y.assign(box_count, 0.0);

        for (uint32_t i = 0; i < box_count; ++i) {
            if (!finite_box(boxes[i])) {
                return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
            }

            double center_x = 0.0;
            double center_y = 0.0;
            if (!box_center(boxes[i], center_x, center_y)) {
                // Preserve the reference behavior for finite endpoints whose
                // binary64 center overflows: they can never pass a finite
                // Euclidean radius predicate, so omit them from the broad phase.
                continue;
            }

            int64_t cell_x = 0;
            int64_t cell_y = 0;
            if (!to_cell(center_x, cell_size, cell_x) ||
                !to_cell(center_y, cell_size, cell_y)) {
                return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
            }

            index->center_x[i] = center_x;
            index->center_y[i] = center_y;
            index->grid[Cell{cell_x, cell_y}].push_back(i);
        }

        *out_index = index.release();
        return PHOTONX_NATIVE_OK;
    } catch (...) {
        return PHOTONX_NATIVE_INTERNAL_ERROR;
    }
}

extern "C" void photonx_point_index_destroy(photonx_point_index* index) {
    delete index;
}

extern "C" int photonx_point_index_radius_candidates(
    const photonx_point_index* index,
    const photonx_point_query* queries,
    uint32_t query_count,
    photonx_query_match* out_matches,
    uint32_t out_capacity,
    uint32_t* out_count
) {
    if (index == nullptr || out_count == nullptr ||
        (query_count != 0U && queries == nullptr)) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }

    *out_count = 0U;

    try {
        std::vector<photonx_query_match> matches;

        for (uint32_t q = 0; q < query_count; ++q) {
            const double x = queries[q].x;
            const double y = queries[q].y;
            const double radius = queries[q].radius;
            if (!std::isfinite(x) || !std::isfinite(y) ||
                !std::isfinite(radius) || radius < 0.0) {
                return PHOTONX_NATIVE_INVALID_ARGUMENT;
            }

            photonx_aabb query_box{
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            };
            if (!finite_box(query_box)) {
                return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
            }

            int64_t min_x = 0;
            int64_t min_y = 0;
            int64_t max_x = 0;
            int64_t max_y = 0;
            if (!query_cell_bounds(
                    query_box,
                    index->cell_size,
                    min_x,
                    min_y,
                    max_x,
                    max_y)) {
                return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
            }

            for (int64_t cell_x = min_x;; ++cell_x) {
                for (int64_t cell_y = min_y;; ++cell_y) {
                    const auto it = index->grid.find(Cell{cell_x, cell_y});
                    if (it != index->grid.end()) {
                        for (const uint32_t point : it->second) {
                            if (index->center_x[point] >= query_box.min_x &&
                                index->center_x[point] <= query_box.max_x &&
                                index->center_y[point] >= query_box.min_y &&
                                index->center_y[point] <= query_box.max_y) {
                                matches.push_back(photonx_query_match{q, point});
                            }
                        }
                    }
                    if (cell_y == max_y) {
                        break;
                    }
                }
                if (cell_x == max_x) {
                    break;
                }
            }
        }

        std::sort(
            matches.begin(),
            matches.end(),
            [](const photonx_query_match& a, const photonx_query_match& b) {
                return a.query < b.query ||
                       (a.query == b.query && a.point < b.point);
            }
        );

        if (matches.size() >
            static_cast<std::size_t>(std::numeric_limits<uint32_t>::max())) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        const uint32_t required = static_cast<uint32_t>(matches.size());
        *out_count = required;
        if (required == 0U) {
            return PHOTONX_NATIVE_OK;
        }

        if (out_matches == nullptr || out_capacity < required) {
            return PHOTONX_NATIVE_BUFFER_TOO_SMALL;
        }

        std::copy(matches.begin(), matches.end(), out_matches);
        return PHOTONX_NATIVE_OK;
    } catch (...) {
        return PHOTONX_NATIVE_INTERNAL_ERROR;
    }
}
