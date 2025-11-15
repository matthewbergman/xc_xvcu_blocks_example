import os
import sys
import shutil
import argparse
import pathlib
import re

import cantools
from cantools.subparsers import generate_c_source

cli_parser = argparse.ArgumentParser(prog="block_gen", description='Generage xVCU block from a DBC file')
cli_parser.add_argument('name', metavar='name', type=str, help='Block name')
cli_parser.add_argument('--nickname', metavar='nickname', type=str, help='Short block name')
cli_parser.add_argument('--dbc', metavar='dbc', type=pathlib.Path, help='DBC file', required=False)
cli_parser.add_argument('-i', type=str, help="Input IDs to include", required=False)
cli_parser.add_argument('-o', type=str, help="Output IDs to include", required=False)

args = cli_parser.parse_args()
block_name = args.name
if args.nickname != None:
    block_nickname = args.nickname
else:
    block_nickname = block_name.lower()

input_ids = []
output_ids = []

### Helper functions
def _canonical(value: str) -> str:
    """Replace anything but 'a-z', 'A-Z' and '0-9' with '_'.

    """

    return re.sub(r'[^a-zA-Z0-9]', '_', value)


def camel_to_snake_case(value: str) -> str:
    value = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', value)
    value = re.sub(r'(_+)', '_', value)
    value = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', value).lower()
    value = _canonical(value)

    return value

def get_signal_type(signal):
    if signal.scale != 1:
        return "float"
    elif signal.is_signed:
        if signal.length <= 8:
            return "int8_t"
        elif signal.length <= 16:
            return "int16_t"
        elif signal.length <= 32:
            return "int32_t"
    else:
        if signal.length <= 8:
            return "uint8_t"
        elif signal.length <= 16:
            return "uint16_t"
        elif signal.length <= 32:
            return "uint32_t"
    return "float"

### Parse DBC if provided

if args.dbc is not None:
    try:
        if len(args.i) > 0:
            for can_id in args.i.split(','):
                if "0x" in can_id:
                    can_id = int(can_id,16)
                else:
                    can_id = int(can_id)
                input_ids.append(can_id)
    except:
        pass
    
    try:
        if len(args.o) > 0:
            for can_id in args.o.split(','):
                if "0x" in can_id:
                    can_id = int(can_id,16)
                else:
                    can_id = int(can_id)
                output_ids.append(can_id)
    except:
        pass

    try:
        dbc = cantools.database.load_file(args.dbc, database_format='dbc', cache_dir=None)
    except:
        print("Failed to open DBC: "+args.dbc)
        sys.exit(1)


# Make directories
root_dirname = "xvcu_"+block_name
tests_dirname = os.path.join(root_dirname, "blocks", block_name, "tests")
src_dirname = os.path.join(root_dirname, "blocks", block_name, "src")
can_dirname = os.path.join(src_dirname, "can")
cmake_dirname = os.path.join(root_dirname, "cmake")
os.makedirs(root_dirname, exist_ok=True)
os.makedirs(tests_dirname, exist_ok=True)
os.makedirs(src_dirname, exist_ok=True)
os.makedirs(can_dirname, exist_ok=True)
os.makedirs(cmake_dirname, exist_ok=True)

# Move over common files
shutil.copy2("../"+".gitignore", os.path.join(root_dirname, ".gitignore"))
shutil.copy2("../"+"winbuild.cmd", os.path.join(root_dirname, "winbuild.cmd"))
shutil.copy2("../"+"cmake/clang-tools.cmake", os.path.join(cmake_dirname, "clang-tools.cmake"))

# generate CMakeLists.txt
cmake_str = f"""cmake_minimum_required(VERSION 3.22)

project(xvcu_{block_name}_library LANGUAGES C)
set(SOURCE_DIR ${{PROJECT_SOURCE_DIR}})

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
"""
cmake_filename = os.path.join(root_dirname, "CMakeLists.txt")
cmake_file = open(cmake_filename,"w")
cmake_file.write(cmake_str)
cmake_file.close()

# Generate README
readme_str = f"""# xVCU {block_name} block library

This library contains an xVCU block generated using the `block_gen.py` script. 
"""
readme_filename = os.path.join(root_dirname, "README.md")
readme_file = open(readme_filename,"w")
readme_file.write(readme_str)
readme_file.close()

# Generate cmake file
cmake_block_str = f"""add_library({block_name}_library STATIC
	${{SOURCE_DIR}}/blocks/{block_name}/src/{block_name}.c
"""
if (args.dbc is not None) and (len(input_ids) > 0 or len(output_ids) > 0):
    cmake_block_str += f"""    ${{SOURCE_DIR}}/blocks/{block_name}/src/can/{block_nickname}.c
"""
cmake_block_str += ")"

cmake_block_filename = os.path.join(cmake_dirname, "example_block.cmake")
cmake_block_file = open(cmake_block_filename,"w")
cmake_block_file.write(cmake_block_str)
cmake_block_file.close()

# Generate block files

def h_file_preamble(block_name):
    preamble = f"""/*
 * {block_name}.h
 *
 *  Created on: TODAY
 *      Author: ME
 *
 *  Version: 0.1
 */

#ifndef {block_name.upper()}_BLOCK_H_
#define {block_name.upper()}_BLOCK_H_

#include <stdint.h>
#include <stdbool.h>

"""
    return preamble

def h_file_input_struct(block_name):
    struct_def = "struct "+block_name+"_inputs_t {\n"
    return struct_def

def h_file_output_struct(block_name):
    struct_def = "struct "+block_name+"_outputs_t {\n"
    return struct_def

def h_file_config_struct(block_name):
    struct_def = f"""struct {block_name}_config_t {{
	uint8_t ticks_per_s;
	void (*can_send)(uint32_t id, bool ext, uint8_t len, uint8_t* buffer);
}};

struct {block_name}_internal_t {{
	uint16_t tick_counter;
    uint16_t can_tick_counter;
}};

"""
    return struct_def

def h_file_block_struct(block_name):
    struct_def = f"""struct {block_name}_data_t {{
	struct {block_name}_inputs_t inputs;
	struct {block_name}_outputs_t outputs;
    struct {block_name}_internal_t internal;
	struct {block_name}_config_t config;
}};

"""
    return struct_def

def h_file_funs(block_name):
    funs = f"""void {block_name}_init(struct {block_name}_data_t* data);
void {block_name}_parse_can(uint32_t can_id, uint8_t* buf, struct {block_name}_data_t* data);
void {block_name}_tick(struct {block_name}_data_t* data);

#endif

"""
    return funs

h_str = h_file_preamble(block_name)

if len(input_ids) > 0:
    h_str += h_file_input_struct(block_name)
    for id in input_ids:
        msg = dbc.get_message_by_frame_id(id)
        if msg is None:
            print("Input ID 0x%X not found in DBC"%(id))
            continue
        for signal in msg.signals:
            h_str += "\t"+get_signal_type(signal)+" "+camel_to_snake_case(signal.name)+";\n"
    h_str += "};\n\n"

if len(output_ids) > 0:
    h_str += h_file_output_struct(block_name)
    for id in output_ids:
        msg = dbc.get_message_by_frame_id(id)
        if msg is None:
            print("Input ID 0x%X not found in DBC"%(id))
            continue
        for signal in msg.signals:
            h_str += "\t"+get_signal_type(signal)+" "+camel_to_snake_case(signal.name)+";\n"
    h_str += "\tuint8_t timeout;\n"
    h_str += "};\n\n"

h_str += h_file_config_struct(block_name)
h_str += h_file_block_struct(block_name)
h_str += h_file_funs(block_name)

block_h_filename = os.path.join(src_dirname, block_name+".h")
h_file = open(block_h_filename,"w")
h_file.write(h_str)
h_file.close()

c_file_str = f"""
/*
 * {block_name}.c
 *
 *  Created on: TODAY
 *      Author: ME
 *
 *  Version: 0.1
 */

#include <math.h>

#include "{block_name}.h"
#include "can/{block_nickname}.h"

void {block_name}_init(struct {block_name}_data_t* data)
{{
    data->config.ticks_per_s = 100;
}}

void {block_name}_parse_can(uint32_t can_id, uint8_t* buf, struct {block_name}_data_t* data)
{{
"""
if len(output_ids) > 0:
    for id in output_ids:
        msg = dbc.get_message_by_frame_id(id)
        if msg is None:
            print("Input ID 0x%X not found in DBC"%(id))
            continue
        c_file_str += f"    if (can_id == 0x{msg.frame_id:X}) {{\n"
        c_file_str += f"        struct {block_nickname}_{camel_to_snake_case(msg.name)}_t s;\n"
        c_file_str += f"        {block_nickname}_{camel_to_snake_case(msg.name)}_unpack(&s, buf, {msg.length});\n"

        for signal in msg.signals:
            c_file_str += f"        data->outputs.{camel_to_snake_case(signal.name)} = "
            if signal.scale != 1 or signal.offset != 0:
                c_file_str += f"""{block_nickname}_{camel_to_snake_case(msg.name)}_{camel_to_snake_case(signal.name)}_decode(s.{camel_to_snake_case(signal.name)})"""
            else:
                c_file_str += f"""s.{camel_to_snake_case(signal.name)}"""
            c_file_str += ";\n"

        c_file_str += "\t}\n"

c_file_str += f"""
}}

void {block_name}_tick(struct {block_name}_data_t* data)
{{
"""

if len(input_ids) > 0:
    counter = 0
    for id in input_ids:
        msg = dbc.get_message_by_frame_id(id)
        if msg is None:
            print("Input ID 0x%X not found in DBC"%(id))
            continue
        c_file_str += f"\tif (data->internal.tick_counter % {len(input_ids)} == {counter})\n\t\t{{\n"
        c_file_str += f"\t\tstruct {block_nickname}_{camel_to_snake_case(msg.name)}_t s;\n"
        for signal in msg.signals:
            if signal.scale != 1 or signal.offset != 0:
                c_file_str += f"""\t\ts.{camel_to_snake_case(signal.name)} = {block_nickname}_{camel_to_snake_case(msg.name)}_{camel_to_snake_case(signal.name)}_encode(data->inputs.{camel_to_snake_case(signal.name)});\n"""
            else:
                c_file_str += f"""\t\ts.{camel_to_snake_case(signal.name)} = data->inputs.{camel_to_snake_case(signal.name)};\n"""
        c_file_str += f"""\t\tuint8_t buf[8];
        {block_nickname}_{camel_to_snake_case(msg.name)}_pack(buf, &s, {msg.length});
        data->config.can_send(0x{msg.frame_id:X}, {"true" if msg.is_extended_frame else "false"}, {msg.length}, buf);
    }}
"""
        counter += 1

c_file_str += f"""
    if (data->internal.can_tick_counter >= (data->config.ticks_per_s * 2)) {{
        data->outputs.timeout = 1;
"""

if len(input_ids) > 0:
    counter = 0
    for id in input_ids:
        msg = dbc.get_message_by_frame_id(id)
        if msg is None:
            continue
        for signal in msg.signals:
            c_file_str += f"\t\tdata->inputs.{camel_to_snake_case(signal.name)} = 0;\n"

c_file_str += f"""
    }}
    else
    {{
        data->outputs.timeout = 0;
    }}

    if (data->internal.can_tick_counter < 0xFFF0)
    {{
        data->internal.can_tick_counter++;
    }}

    data->internal.tick_counter++;
}}
"""

block_c_filename = os.path.join(src_dirname, block_name+".c")
c_file = open(block_c_filename,"w")
c_file.write(c_file_str)
c_file.close()

if args.dbc is not None and (len(input_ids) > 0 or len(output_ids) > 0):
    header, source, fuzzer_source, fuzzer_makefile = generate_c_source.generate(dbc, block_nickname, block_nickname+".h", block_nickname+".c", block_nickname+".c", use_float=True)

    can_h_filename = os.path.join(can_dirname, block_nickname+".h")
    can_h_file = open(can_h_filename,"w")
    can_h_file.write(header)
    can_h_file.close()

    can_c_filename = os.path.join(can_dirname, block_nickname+".c")
    can_c_file = open(can_c_filename,"w")
    can_c_file.write(source)
    can_c_file.close()

test_file_str = f"""
#include <gtest/gtest.h>

extern "C" {{
#include "../src/{block_name}.h"
}}

class {block_name}_tests : public testing::Test {{}};

TEST_F({block_name}_tests, test_init) {{
    struct {block_name}_data_t data;

    {block_name}_init(&data);

    EXPECT_EQ(data.config.ticks_per_sec, 100); 
}}
"""

test_filename = os.path.join(tests_dirname, "test_"+block_name+".cpp")
test_file = open(test_filename,"w")
test_file.write(test_file_str)
test_file.close()

