/*
 * example_block.h
 *
 *  Created on: TODAY
 *      Author: ME
 *
 *  Version: 0.1
 */

#ifndef EXAMPLE_BLOCK_H_
#define EXAMPLE_BLOCK_H_

#include <stdint.h>
#include <stdbool.h>

/*
* Inputs can be updated from links to other blocks or measurements each time the block's loop is called
*/
struct example_block_inputs_t {
	bool inputs_bool;       // Note: this will be treated like a unit8 in xCal/YACP
    uint8_t inputs_uint8;
    uint16_t inputs_uint16;
    uint32_t inputs_uint32;
    int8_t inputs_int8;
    int16_t inputs_int16;
    int32_t inputs_int32;
	float inputs_float;		// Unit:RPM Note:Notes wll show up as tooltips in xVCU
};

/*
* Outputs send data from this block to other blocks or measurements
*/
struct example_block_outputs_t {
    bool outputs_bool;
    uint8_t outputs_uint8;
    uint16_t outputs_uint16;
    uint32_t outputs_uint32;
    int8_t outputs_int8;
    int16_t outputs_int16;
    int32_t outputs_int32;
	float outputs_float;
};

/*
* Internal data is not seen by other blocks and is used for block housekeeping
*/
struct example_block_internal_t {
    bool internal_bool;
    uint8_t internal_uint8;
    uint16_t internal_uint16;
    uint32_t internal_uint32;
    int8_t internal_int8;
    int16_t internal_int16;
    int32_t internal_int32;
	float internal_float;
};

/*
* Configuration items are set once at startup, typically from NVM. 
* There are two special config items:
*    ticks_per_s - this is the rate at which the block's tick function is called
*    can_send - if this block needs to send data on a CAN bus use this function. Omit if this block does not use CAN.
*/
struct example_block_config_t {
	uint8_t ticks_per_s;
	void (*can_send)(uint32_t id, bool ext, uint8_t len, uint8_t* buffer);

    bool config_bool;
    uint8_t config_uint8;
    uint16_t config_uint16;
    uint32_t config_uint32;
    int8_t config_int8;
    int16_t config_int16;
    int32_t config_int32;
	float config_float;
};

struct example_block_data_t {
	struct example_block_inputs_t inputs;
	struct example_block_outputs_t outputs;
	struct example_block_internal_t internal;
	struct example_block_config_t config;
};

// Called once at startup
void example_block_init(struct example_block_data_t* data);
// Called whenever a CAN packet is received on the bus this block is connected to.  Omit if this block does not use CAN.
void example_block_parse_can(uint32_t can_id, uint8_t* buf, struct example_block_data_t* data);
// Called once per loop cycle, after this block's inputs are set and before this block's outputs are sent on to other blocks
void example_block_tick(struct example_block_data_t* data);

#endif
