#include "photonx_native.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <unordered_map>
#include <vector>

namespace {

constexpr uint32_t kAbiVersion = 1;
constexpr long double kMaxCellsPerBox = 1000000.0L;
constexpr long double kMaxTotalInsertedCells = 20000000.0L;

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

bool finite_box(const photonx_aabb& box) noexcept {
    return std::isfinite(box.min_x) && std::isfinite(box.min_y) &&
           std::isfinite(box.max_x) && std::isfinite(box.max_y) &&
           box.min_x <= box.max_x && box.min_y <= box.max_y;
}

bool to_cell(double coordinate, double cell_size, int64_t& out) noexcept {
    // Match Python SpatialHashIndex._range exactly: both operands are Python
    // floats, so division is IEEE-754 binary64 before floor().  Promoting the
    // operands to long double changes rounding at exact cell boundaries and
    // can make the native broad phase omit candidates that Python includes.
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

bool cell_bounds(
    const photonx_aabb& box,
    double cell_size,
    int64_t& min_x,
    int64_t& min_y,
    int64_t& max_x,
    int64_t& max_y,
    long double& cell_count
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

    cell_count = width * height;
    return std::isfinite(cell_count) && cell_count <= kMaxCellsPerBox;
}

bool intersects(const photonx_aabb& a, const photonx_aabb& b) noexcept {
    return !(a.max_x < b.min_x || b.max_x < a.min_x ||
             a.max_y < b.min_y || b.max_y < a.min_y);
}

bool expanded_box(
    const photonx_aabb& box,
    double tolerance,
    photonx_aabb& out
) noexcept {
    out.min_x = box.min_x - tolerance;
    out.min_y = box.min_y - tolerance;
    out.max_x = box.max_x + tolerance;
    out.max_y = box.max_y + tolerance;
    return finite_box(out);
}

int compute_pairs(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double tolerance,
    double cell_size,
    std::vector<photonx_pair>& pairs
) {
    if ((box_count != 0U && boxes == nullptr) ||
        !std::isfinite(tolerance) || tolerance < 0.0 ||
        !std::isfinite(cell_size) || cell_size <= 0.0) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }

    using Grid =
        std::unordered_map<Cell, std::vector<uint32_t>, CellHash>;
    Grid grid;
    long double total_inserted_cells = 0.0L;

    for (uint32_t i = 0; i < box_count; ++i) {
        if (!finite_box(boxes[i])) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        int64_t min_x = 0;
        int64_t min_y = 0;
        int64_t max_x = 0;
        int64_t max_y = 0;
        long double cell_count = 0.0L;
        if (!cell_bounds(
                boxes[i], cell_size, min_x, min_y, max_x, max_y, cell_count)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        total_inserted_cells += cell_count;
        if (total_inserted_cells > kMaxTotalInsertedCells) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        for (int64_t x = min_x;; ++x) {
            for (int64_t y = min_y;; ++y) {
                grid[Cell{x, y}].push_back(i);
                if (y == max_y) {
                    break;
                }
            }
            if (x == max_x) {
                break;
            }
        }
    }

    std::vector<uint32_t> visited(box_count, 0U);
    uint32_t generation = 0U;

    for (uint32_t i = 0; i < box_count; ++i) {
        photonx_aabb query{};
        if (!expanded_box(boxes[i], tolerance, query)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        int64_t min_x = 0;
        int64_t min_y = 0;
        int64_t max_x = 0;
        int64_t max_y = 0;
        long double cell_count = 0.0L;
        if (!cell_bounds(
                query, cell_size, min_x, min_y, max_x, max_y, cell_count)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        ++generation;
        if (generation == 0U) {
            std::fill(visited.begin(), visited.end(), 0U);
            generation = 1U;
        }

        for (int64_t x = min_x;; ++x) {
            for (int64_t y = min_y;; ++y) {
                const auto it = grid.find(Cell{x, y});
                if (it != grid.end()) {
                    for (const uint32_t candidate : it->second) {
                        if (candidate <= i || visited[candidate] == generation) {
                            continue;
                        }
                        visited[candidate] = generation;
                        if (intersects(boxes[candidate], query)) {
                            pairs.push_back(photonx_pair{i, candidate});
                        }
                    }
                }
                if (y == max_y) {
                    break;
                }
            }
            if (x == max_x) {
                break;
            }
        }
    }

    std::sort(
        pairs.begin(),
        pairs.end(),
        [](const photonx_pair& a, const photonx_pair& b) {
            return a.first < b.first ||
                   (a.first == b.first && a.second < b.second);
        }
    );

    return PHOTONX_NATIVE_OK;
}

}  // namespace

extern "C" uint32_t photonx_native_abi_version(void) {
    return kAbiVersion;
}

extern "C" int photonx_candidate_pairs(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double tolerance,
    double cell_size,
    photonx_pair* out_pairs,
    uint32_t out_capacity,
    uint32_t* out_count
) {
    if (out_count == nullptr) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }

    *out_count = 0U;

    try {
        std::vector<photonx_pair> pairs;
        const int status =
            compute_pairs(boxes, box_count, tolerance, cell_size, pairs);
        if (status != PHOTONX_NATIVE_OK) {
            return status;
        }

        if (pairs.size() >
            static_cast<std::size_t>(std::numeric_limits<uint32_t>::max())) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        const uint32_t required = static_cast<uint32_t>(pairs.size());
        *out_count = required;

        if (required == 0U) {
            return PHOTONX_NATIVE_OK;
        }

        if (out_pairs == nullptr || out_capacity < required) {
            return PHOTONX_NATIVE_BUFFER_TOO_SMALL;
        }

        std::copy(pairs.begin(), pairs.end(), out_pairs);
        return PHOTONX_NATIVE_OK;
    } catch (...) {
        return PHOTONX_NATIVE_INTERNAL_ERROR;
    }
}
