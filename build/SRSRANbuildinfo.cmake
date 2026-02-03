
execute_process(
COMMAND git rev-parse --abbrev-ref HEAD
WORKING_DIRECTORY "/home/jetsonnx/SDR_ABS_nano"
OUTPUT_VARIABLE GIT_BRANCH
OUTPUT_STRIP_TRAILING_WHITESPACE
)

execute_process(
COMMAND git log -1 --format=%h
WORKING_DIRECTORY "/home/jetsonnx/SDR_ABS_nano"
OUTPUT_VARIABLE GIT_COMMIT_HASH
OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "Generating build_info.h")
configure_file(
  /home/jetsonnx/SDR_ABS_nano/lib/include/srsran/build_info.h.in
  /home/jetsonnx/SDR_ABS_nano/build/lib/include/srsran/build_info.h
)
