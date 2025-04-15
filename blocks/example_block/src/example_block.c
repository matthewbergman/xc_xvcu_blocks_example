/*
 * example_block.c
 *
 *  Created on: TODAY
 *      Author: ME
 *
 *  Version: 0.1
 */

#include <math.h>

#include "example_block.h"

void example_block_init(struct example_block_data_t* data)
{
    data->config.config_uint8 = 1;
}

void example_block_parse_can(uint32_t can_id, uint8_t* buf, struct example_block_data_t* data)
{
    data->outputs.outputs_uint8 = buf[0];
}

void example_block_tick(struct example_block_data_t* data)
{
    data->outputs.outputs_bool = data->config.config_bool;
    data->outputs.outputs_uint8 = data->config.config_uint8;
    data->outputs.outputs_uint16 = data->config.config_uint16;
    data->outputs.outputs_uint32 = data->config.config_uint32;
    data->outputs.outputs_int8 = data->config.config_int8;
    data->outputs.outputs_int16 = data->config.config_int16;
    data->outputs.outputs_int32 = data->config.config_int32;
    data->outputs.outputs_float = data->config.config_float;
}