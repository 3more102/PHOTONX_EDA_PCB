cmake_minimum_required(VERSION 3.20)
project(photonx_native LANGUAGES CXX)

add_library(photonx_native SHARED
    src/spatial_pairs.cpp
    src/point_index.cpp
)

target_compile_features(photonx_native PRIVATE cxx_std_17)
target_compile_definitions(photonx_native PRIVATE PHOTONX_NATIVE_BUILD=1)
target_include_directories(photonx_native
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

set_target_properties(photonx_native PROPERTIES
    CXX_EXTENSIONS OFF
    POSITION_INDEPENDENT_CODE ON
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

if(MSVC)
    target_compile_options(photonx_native PRIVATE /W4 /permissive-)
else()
    target_compile_options(photonx_native PRIVATE -Wall -Wextra -Wpedantic)
endif()
