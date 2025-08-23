cmake_minimum_required(VERSION 3.15)
project(loudstream)

set(BUILD_SHARED_LIBS ON CACHE BOOL "" FORCE)

set(PY_IMPORT_NAME loudstream)

add_subdirectory(extern/libebur128)

install(TARGETS ebur128
    LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME}/lib
    ARCHIVE DESTINATION ${SKBUILD_PROJECT_NAME}/lib
    RUNTIME DESTINATION ${SKBUILD_PROJECT_NAME}/lib
)

