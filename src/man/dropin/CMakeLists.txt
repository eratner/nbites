cmake_minimum_required(VERSION 2.8.3)

# Set source files here that need to be compiled.
set(DROPIN_SRCS DropInModule)

# Add project as a library.
add_library(
  dropin
  STATIC
  ${DROPIN_SRCS}
)

# Link project to appropriate libraries.
target_link_libraries(dropin
  support
  portals
  messages
  ${ALCOMMON_LIBRARIES}
)
