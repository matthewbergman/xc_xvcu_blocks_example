cmake_minimum_required(VERSION 3.22)
include(test-and-coverage.cmake)
project(application_tests LANGUAGES C CXX)
set(TEST_TARGET example_block_tests)
set(SOURCE_DIR ${PROJECT_SOURCE_DIR}/..)

include(../cmake/xvcu_library.cmake)

add_executable(${TEST_TARGET}
	${SOURCE_DIR}/blocks/example_block/tests/test_example_block.cpp
)

target_link_libraries(${TEST_TARGET} PRIVATE
	example_block_library
	GTest::gtest_main
	GTest::gmock
)

enable_testing()
include(GoogleTest)
gtest_discover_tests(${TEST_TARGET})
add_custom_command(TARGET ${TEST_TARGET} POST_BUILD
	COMMAND ctest ARGS --output-on-failure
)
