cmake_minimum_required(VERSION 3.22)

project(xvcu_library LANGUAGES C)
set(SOURCE_DIR ${PROJECT_SOURCE_DIR})

include(cmake/xvcu_library.cmake)

add_compile_options(
	#-pedantic
	#-pedantic-errors
	#-Wconversion
	#-Wfloat-equal
    	-Wall
	-Wextra
	-Werror
	-Wuninitialized
	-Wunused
	-Wshadow
	-Wpointer-arith
	-Wlogical-op
	-Waggregate-return
)

add_compile_options(
	-O0
	-g3
)
