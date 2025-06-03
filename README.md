# xc_xvcu_blocks_example
Example xVCU block library

Use this example to create your own block libraries. Simply replace the string 'example_block' with your unique block name everywhere it is found in this example.


- Add a folder matching the block name in the blocks folder, i.e. blocks/***block_name***
- Add src and tests folders in the new blocks/***block_name*** folder
- Add the ***block_name***.c and ***block_name***.h file into the src folder
- Copy the example test_example_block.cpp file and copy it into the tests blocks/***block_name***/tests folder
- Replace example_block string with your ***block_name*** in the test_example_block.cpp file
- Rename test_example_block.cpp to test_***block_name***.cpp
- Add the path to test_***block_name***.cpp in tests/CMakeLists.txt in the add_executable section (see example in this project)
- Add path to the ***block_name***.c file in the cmake/xvcu_library.cmake file under the add_library section (see example in this project)
- Test that the library builds by running build.cmd (you may need to delete the build directory first) 