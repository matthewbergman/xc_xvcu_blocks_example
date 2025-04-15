SETLOCAL
SET TESTS_DIRECTORY=build\tests

if not exist %TESTS_DIRECTORY%\  (
	cmake -S ./tests -B %TESTS_DIRECTORY% -G"Unix Makefiles"
)
cmake --build %TESTS_DIRECTORY%
ENDLOCAL

