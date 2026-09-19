#include "photonx_native.h"

#include <array>
#include <cstdint>
#include <iostream>
#include <limits>

namespace {

int failures = 0;

void expect(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        ++failures;
    }
}

void test_candidate_pairs_contract() {
    const std::array<photonx_aabb, 3> boxes{{
        {0.0, 0.0, 1.0, 1.0},
        {1.0, 0.0, 2.0, 1.0},
        {3.0, 3.0, 4.0, 4.0},
    }};

    uint32_t required = 0;
    int status = photonx_candidate_pairs(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        0.0,
        1.0,
        nullptr,
        0,
        &required
    );
    expect(
        status == PHOTONX_NATIVE_BUFFER_TOO_SMALL,
        "candidate sizing call reports BUFFER_TOO_SMALL"
    );
    expect(required == 1U, "candidate sizing call reports exact count");

    std::array<photonx_pair, 1> out{};
    uint32_t written = 0;
    status = photonx_candidate_pairs(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        0.0,
        1.0,
        out.data(),
        static_cast<uint32_t>(out.size()),
        &written
    );
    expect(status == PHOTONX_NATIVE_OK, "candidate fill call succeeds");
    expect(written == 1U, "candidate fill count matches sizing count");
    expect(
        out[0].first == 0U && out[0].second == 1U,
        "candidate output is canonical and deterministic"
    );

    status = photonx_candidate_pairs(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        0.0,
        1.0,
        out.data(),
        0,
        &written
    );
    expect(
        status == PHOTONX_NATIVE_BUFFER_TOO_SMALL,
        "insufficient candidate capacity is reported"
    );

    status = photonx_candidate_pairs(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        -0.1,
        1.0,
        nullptr,
        0,
        &written
    );
    expect(
        status == PHOTONX_NATIVE_INVALID_ARGUMENT,
        "negative candidate tolerance is invalid"
    );

    status = photonx_candidate_pairs(
        nullptr,
        1U,
        0.0,
        1.0,
        nullptr,
        0,
        &written
    );
    expect(
        status == PHOTONX_NATIVE_INVALID_ARGUMENT,
        "non-empty candidate input requires boxes"
    );

    status = photonx_candidate_pairs(
        nullptr,
        0U,
        0.0,
        1.0,
        nullptr,
        0,
        &written
    );
    expect(
        status == PHOTONX_NATIVE_OK && written == 0U,
        "empty candidate input succeeds"
    );

    status = photonx_candidate_pairs(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        0.0,
        1.0,
        nullptr,
        0,
        nullptr
    );
    expect(
        status == PHOTONX_NATIVE_INVALID_ARGUMENT,
        "candidate out_count is required"
    );
}

void test_radius_contract() {
    const std::array<photonx_aabb, 3> boxes{{
        {0.0, 0.0, 0.0, 0.0},
        {1.0, 0.0, 1.0, 0.0},
        {2.0, 0.0, 2.0, 0.0},
    }};
    const std::array<photonx_point_query, 2> queries{{
        {0.0, 0.0, 1.0},
        {2.0, 0.0, 0.0},
    }};

    uint32_t required = 0;
    int status = photonx_point_radius_candidates(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        queries.data(),
        static_cast<uint32_t>(queries.size()),
        1.0,
        nullptr,
        0,
        &required
    );
    expect(
        status == PHOTONX_NATIVE_BUFFER_TOO_SMALL,
        "radius sizing call reports BUFFER_TOO_SMALL"
    );
    expect(required == 3U, "radius sizing call reports exact broad-phase count");

    std::array<photonx_query_match, 3> out{};
    uint32_t written = 0;
    status = photonx_point_radius_candidates(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        queries.data(),
        static_cast<uint32_t>(queries.size()),
        1.0,
        out.data(),
        static_cast<uint32_t>(out.size()),
        &written
    );
    expect(status == PHOTONX_NATIVE_OK, "radius fill call succeeds");
    expect(written == 3U, "radius fill count matches sizing count");
    expect(
        out[0].query == 0U && out[0].point == 0U,
        "radius results begin with query 0 point 0"
    );
    expect(
        out[1].query == 0U && out[1].point == 1U,
        "radius results preserve point ordering"
    );
    expect(
        out[2].query == 1U && out[2].point == 2U,
        "radius results preserve query ordering"
    );

    const photonx_point_query negative_radius{0.0, 0.0, -1.0};
    status = photonx_point_radius_candidates(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        &negative_radius,
        1U,
        1.0,
        nullptr,
        0,
        &written
    );
    expect(
        status == PHOTONX_NATIVE_INVALID_ARGUMENT,
        "negative C-ABI radius is invalid"
    );

    status = photonx_point_radius_candidates(
        boxes.data(),
        static_cast<uint32_t>(boxes.size()),
        nullptr,
        1U,
        1.0,
        nullptr,
        0,
        &written
    );
    expect(
        status == PHOTONX_NATIVE_INVALID_ARGUMENT,
        "non-empty radius input requires query storage"
    );
}

void test_unsupported_ranges_fail_closed() {
    const photonx_aabb nan_box{
        std::numeric_limits<double>::quiet_NaN(),
        0.0,
        0.0,
        0.0,
    };
    uint32_t count = 0;
    int status = photonx_candidate_pairs(
        &nan_box,
        1U,
        0.0,
        1.0,
        nullptr,
        0,
        &count
    );
    expect(
        status == PHOTONX_NATIVE_UNSUPPORTED_RANGE,
        "non-finite boxes fail closed"
    );

    const photonx_aabb oversized{0.0, 0.0, 1000.0, 1000.0};
    status = photonx_candidate_pairs(
        &oversized,
        1U,
        0.0,
        1.0,
        nullptr,
        0,
        &count
    );
    expect(
        status == PHOTONX_NATIVE_UNSUPPORTED_RANGE,
        "per-box spatial work limit fails closed"
    );

    const photonx_point_query huge_query{0.0, 0.0, 1000.0};
    const photonx_aabb origin{0.0, 0.0, 0.0, 0.0};
    status = photonx_point_radius_candidates(
        &origin,
        1U,
        &huge_query,
        1U,
        1.0,
        nullptr,
        0,
        &count
    );
    expect(
        status == PHOTONX_NATIVE_UNSUPPORTED_RANGE,
        "radius spatial work limit fails closed"
    );
}

}  // namespace

int main() {
    expect(photonx_native_abi_version() == 2U, "native ABI version remains v2");
    test_candidate_pairs_contract();
    test_radius_contract();
    test_unsupported_ranges_fail_closed();

    if (failures != 0) {
        std::cerr << failures << " native contract assertion(s) failed\n";
        return 1;
    }

    std::cout << "native C ABI contract tests passed\n";
    return 0;
}
