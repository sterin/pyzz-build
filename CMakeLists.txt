cmake_minimum_required(VERSION 3.3.0)

project(pyzz_extension)

include(cmake/pyabc.cmake)

add_subdirectory(abc EXCLUDE_FROM_ALL)

set(ZZ_USE_EXTERNAL_LIBABC TRUE)
add_subdirectory(abc-zz EXCLUDE_FROM_ALL)

add_subdirectory(pywrapper EXCLUDE_FROM_ALL)
add_subdirectory(pyzz EXCLUDE_FROM_ALL)

install_python_module(pyzz/pyzz)

install_target(_pyzz DESTINATION lib/pyzz)
