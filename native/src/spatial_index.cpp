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

using Grid = std::unordered_map<Cell, std::vector<uint32_t>, CellHash>;

struct NativeSpatialIndex {
    double cell_size = 1.0;
    std::vector<photonx_aabb> boxes;
    Grid box_grid;
    std::vector<double> center_x;
    std::vector<double> center_y;
    std::vector<uint8_t> center_valid;
    Grid point_grid;
    bool pair_supported = true;
    bool radius_supported = true;
};

bool finite_box(const photonx_aabb& box) noexcept {
    return std::isfinite(box.min_x) && std::isfinite(box.min_y) &&
           std::isfinite(box.max_x) && std::isfinite(box.max_y) &&
           box.min_x <= box.max_x && box.min_y <= box.max_y;
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

bool box_center(
    const photonx_aabb& box,
    double& center_x,
    double& center_y
) noexcept {
    center_x = (box.min_x + box.max_x) / 2.0;
    center_y = (box.min_y + box.max_y) / 2.0;
    return std::isfinite(center_x) && std::isfinite(center_y);
}

void insert_cells(
    Grid& grid,
    uint32_t item,
    int64_t min_x,
    int64_t min_y,
    int64_t max_x,
    int64_t max_y
) {
    for (int64_t x = min_x;; ++x) {
        for (int64_t y = min_y;; ++y) {
            grid[Cell{x, y}].push_back(item);
            if (y == max_y) {
                break;
            }
        }
        if (x == max_x) {
            break;
        }
    }
}

int build_index(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double cell_size,
    NativeSpatialIndex& index
) {
    if ((box_count != 0U && boxes == nullptr) ||
        !std::isfinite(cell_size) || cell_size <= 0.0) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }

    index.cell_size = cell_size;
    if (box_count == 0U) {
        index.boxes.clear();
    } else {
        index.boxes.assign(boxes, boxes + box_count);
    }
    index.center_x.assign(box_count, 0.0);
    index.center_y.assign(box_count, 0.0);
    index.center_valid.assign(box_count, 0U);

    long double total_inserted_cells = 0.0L;

    for (uint32_t i = 0; i < box_count; ++i) {
        const auto& box = index.boxes[i];
        if (!finite_box(box)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        if (index.pair_supported) {
            int64_t min_x = 0;
            int64_t min_y = 0;
            int64_t max_x = 0;
            int64_t max_y = 0;
            long double cell_count = 0.0L;
            if (!cell_bounds(
                    box,
                    cell_size,
                    min_x,
                    min_y,
                    max_x,
                    max_y,
                    cell_count)) {
                index.pair_supported = false;
                index.box_grid.clear();
            } else {
                total_inserted_cells += cell_count;
                if (total_inserted_cells > kMaxTotalInsertedCells) {
                    index.pair_supported = false;
                    index.box_grid.clear();
                } else {
                    insert_cells(index.box_grid, i, min_x, min_y, max_x, max_y);
                }
            }
        }

        double center_x = 0.0;
        double center_y = 0.0;
        if (!box_center(box, center_x, center_y)) {
            // Finite endpoints can overflow during binary64 center arithmetic.
            // The Python exact-radius predicate cannot accept that +/-inf center
            // for a finite query, so keep it absent from the point grid.
            continue;
        }

        index.center_x[i] = center_x;
        index.center_y[i] = center_y;
        index.center_valid[i] = 1U;

        if (index.radius_supported) {
            int64_t cell_x = 0;
            int64_t cell_y = 0;
            if (!to_cell(center_x, cell_size, cell_x) ||
                !to_cell(center_y, cell_size, cell_y)) {
                index.radius_supported = false;
                index.point_grid.clear();
            } else {
                index.point_grid[Cell{cell_x, cell_y}].push_back(i);
            }
        }
    }

    return PHOTONX_NATIVE_OK;
}

int compute_pairs(
    const NativeSpatialIndex& index,
    double tolerance,
    std::vector<photonx_pair>& pairs
) {
    if (!std::isfinite(tolerance) || tolerance < 0.0) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }
    if (!index.pair_supported) {
        return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
    }

    const uint32_t box_count = static_cast<uint32_t>(index.boxes.size());
    std::vector<uint32_t> visited(box_count, 0U);
    uint32_t generation = 0U;

    for (uint32_t i = 0; i < box_count; ++i) {
        photonx_aabb query{};
        if (!expanded_box(index.boxes[i], tolerance, query)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        int64_t min_x = 0;
        int64_t min_y = 0;
        int64_t max_x = 0;
        int64_t max_y = 0;
        long double cell_count = 0.0L;
        if (!cell_bounds(
                query,
                index.cell_size,
                min_x,
                min_y,
                max_x,
                max_y,
                cell_count)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        ++generation;
        if (generation == 0U) {
            std::fill(visited.begin(), visited.end(), 0U);
            generation = 1U;
        }

        for (int64_t x = min_x;; ++x) {
            for (int64_t y = min_y;; ++y) {
                const auto it = index.box_grid.find(Cell{x, y});
                if (it != index.box_grid.end()) {
                    for (const uint32_t candidate : it->second) {
                        if (candidate == i || visited[candidate] == generation) {
                            continue;
                        }
                        visited[candidate] = generation;
                        if (intersects(index.boxes[candidate], query)) {
                            const uint32_t first = std::min(i, candidate);
                            const uint32_t second = std::max(i, candidate);
                            pairs.push_back(photonx_pair{first, second});
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
    pairs.erase(
        std::unique(
            pairs.begin(),
            pairs.end(),
            [](const photonx_pair& a, const photonx_pair& b) {
                return a.first == b.first && a.second == b.second;
            }
        ),
        pairs.end()
    );
    return PHOTONX_NATIVE_OK;
}

int compute_radius_candidates(
    const NativeSpatialIndex& index,
    const photonx_point_query* queries,
    uint32_t query_count,
    std::vector<photonx_query_match>& matches
) {
    if (query_count != 0U && queries == nullptr) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }
    if (!index.radius_supported) {
        return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
    }

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
        long double cell_count = 0.0L;
        if (!cell_bounds(
                query_box,
                index.cell_size,
                min_x,
                min_y,
                max_x,
                max_y,
                cell_count)) {
            return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
        }

        for (int64_t cell_x = min_x;; ++cell_x) {
            for (int64_t cell_y = min_y;; ++cell_y) {
                const auto it = index.point_grid.find(Cell{cell_x, cell_y});
                if (it != index.point_grid.end()) {
                    for (const uint32_t point : it->second) {
                        if (!index.center_valid[point]) {
                            continue;
                        }
                        if (index.center_x[point] >= query_box.min_x &&
                            index.center_x[point] <= query_box.max_x &&
                            index.center_y[point] >= query_box.min_y &&
                            index.center_y[point] <= query_box.max_y) {
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
    return PHOTONX_NATIVE_OK;
}

template <typename T>
int write_results(
    const std::vector<T>& values,
    T* output,
    uint32_t capacity,
    uint32_t* out_count
) {
    if (out_count == nullptr) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }
    if (values.size() >
        static_cast<std::size_t>(std::numeric_limits<uint32_t>::max())) {
        return PHOTONX_NATIVE_UNSUPPORTED_RANGE;
    }

    const uint32_t required = static_cast<uint32_t>(values.size());
    *out_count = required;
    if (required == 0U) {
        return PHOTONX_NATIVE_OK;
    }
    if (output == nullptr || capacity < required) {
        return PHOTONX_NATIVE_BUFFER_TOO_SMALL;
    }

    std::copy(values.begin(), values.end(), output);
    return PHOTONX_NATIVE_OK;
}

}  // namespace

extern "C" int photonx_spatial_index_create(
    const photonx_aabb* boxes,
    uint32_t box_count,
    double cell_size,
    photonx_spatial_index_handle* out_handle
) {
    if (out_handle == nullptr) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }
    *out_handle = nullptr;

    try {
        auto index = std::make_unique<NativeSpatialIndex>();
        const int status = build_index(boxes, box_count, cell_size, *index);
        if (status != PHOTONX_NATIVE_OK) {
            return status;
        }
        *out_handle = static_cast<photonx_spatial_index_handle>(index.release());
        return PHOTONX_NATIVE_OK;
    } catch (...) {
        return PHOTONX_NATIVE_INTERNAL_ERROR;
    }
}

extern "C" void photonx_spatial_index_destroy(
    photonx_spatial_index_handle handle
) {
    delete static_cast<NativeSpatialIndex*>(handle);
}

extern "C" int photonx_spatial_index_candidate_pairs(
    photonx_spatial_index_handle handle,
    double tolerance,
    photonx_pair* out_pairs,
    uint32_t out_capacity,
    uint32_t* out_count
) {
    if (out_count == nullptr || handle == nullptr) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }
    *out_count = 0U;

    try {
        std::vector<photonx_pair> pairs;
        const int status = compute_pairs(
            *static_cast<NativeSpatialIndex*>(handle),
            tolerance,
            pairs
        );
        if (status != PHOTONX_NATIVE_OK) {
            return status;
        }
        return write_results(pairs, out_pairs, out_capacity, out_count);
    } catch (...) {
        return PHOTONX_NATIVE_INTERNAL_ERROR;
    }
}

extern "C" int photonx_spatial_index_point_radius_candidates(
    photonx_spatial_index_handle handle,
    const photonx_point_query* queries,
    uint32_t query_count,
    photonx_query_match* out_matches,
    uint32_t out_capacity,
    uint32_t* out_count
) {
    if (out_count == nullptr || handle == nullptr) {
        return PHOTONX_NATIVE_INVALID_ARGUMENT;
    }
    *out_count = 0U;

    try {
        std::vector<photonx_query_match> matches;
        const int status = compute_radius_candidates(
            *static_cast<NativeSpatialIndex*>(handle),
            queries,
            query_count,
            matches
        );
        if (status != PHOTONX_NATIVE_OK) {
            return status;
        }
        return write_results(matches, out_matches, out_capacity, out_count);
    } catch (...) {
        return PHOTONX_NATIVE_INTERNAL_ERROR;
    }
}
