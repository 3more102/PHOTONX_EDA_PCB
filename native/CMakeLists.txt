cmake_minimum_required(VERSION 3.20)
project(photonx_native LANGUAGES CXX)

option(PHOTONX_NATIVE_BUILD_TESTS "Build native C ABI contract tests" OFF)
option(PHOTONX_NATIVE_ENABLE_SANITIZERS "Enable ASan/UBSan for native targets" OFF)

function(photonx_configure_native_target target)
    target_compile_features(${target} PRIVATE cxx_std_17)

    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /permissive-)
    else()
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    if(PHOTONX_NATIVE_ENABLE_SANITIZERS)
        if(MSVC)
            message(FATAL_ERROR "PHOTONX native sanitizers currently require GCC or Clang")
        elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
            target_compile_options(
                ${target}
                PRIVATE
                    -fsanitize=address,undefined
                    -fno-omit-frame-pointer
            )
            target_link_options(
                ${target}
                PRIVATE
                    -fsanitize=address,undefined
                    -fno-omit-frame-pointer
            )
        else()
            message(FATAL_ERROR "PHOTONX native sanitizers require GCC or Clang")
        endif()
    endif()
endfunction()

add_library(photonx_native SHARED
    src/spatial_pairs.cpp
)

target_compile_definitions(photonx_native PRIVATE PHOTONX_NATIVE_BUILD=1)
target_include_directories(photonx_native
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)
photonx_configure_native_target(photonx_native)

set_target_properties(photonx_native PROPERTIES
    CXX_EXTENSIONS OFF
    POSITION_INDEPENDENT_CODE ON
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

# Keep the loadable library in one predictable directory on both
# single-config and multi-config generators (for example Visual Studio).
# Without the per-config properties, multi-config generators append
# Release/Debug below the configured output directory.
foreach(config IN ITEMS Debug Release RelWithDebInfo MinSizeRel)
    string(TOUPPER "${config}" config_upper)
    set_target_properties(photonx_native PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY_${config_upper} "${CMAKE_BINARY_DIR}/lib"
        RUNTIME_OUTPUT_DIRECTORY_${config_upper} "${CMAKE_BINARY_DIR}/lib"
        ARCHIVE_OUTPUT_DIRECTORY_${config_upper} "${CMAKE_BINARY_DIR}/lib"
    )
endforeach()

if(PHOTONX_NATIVE_BUILD_TESTS)
    enable_testing()

    add_executable(photonx_native_contract_tests
        tests/spatial_pairs_contract.cpp
    )
    target_link_libraries(photonx_native_contract_tests PRIVATE photonx_native)
    photonx_configure_native_target(photonx_native_contract_tests)

    # Place the contract test beside the shared library so Windows can also
    # locate photonx_native.dll when developers opt into these tests locally.
    set_target_properties(photonx_native_contract_tests PROPERTIES
        CXX_EXTENSIONS OFF
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    )
    foreach(config IN ITEMS Debug Release RelWithDebInfo MinSizeRel)
        string(TOUPPER "${config}" config_upper)
        set_target_properties(photonx_native_contract_tests PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY_${config_upper} "${CMAKE_BINARY_DIR}/lib"
        )
    endforeach()

    add_test(
        NAME photonx_native_contract
        COMMAND photonx_native_contract_tests
    )
endif()
