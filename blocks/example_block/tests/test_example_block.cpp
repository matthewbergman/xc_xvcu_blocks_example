#include <gtest/gtest.h>

extern "C" {
#include "../src/example_block.h"
}

class example_block_tests : public testing::Test {};

TEST_F(example_block_tests, test_init) {
    struct example_block_data_t data;

    example_block_init(&data);

    EXPECT_EQ(data.config.config_uint8, 1); 
}
