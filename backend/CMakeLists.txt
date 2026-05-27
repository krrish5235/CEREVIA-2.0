cmake_minimum_required(VERSION 3.10)
project(mental_health_backend)
set(CMAKE_CXX_STANDARD 17)
include_directories(.)
include_directories(libs/json)
include_directories(libs/json/sqlite)
add_executable(backend
    main.cpp
    ApiServer.cpp
    Database.cpp
    MoodTracker.cpp
    JournalManager.cpp
    Encryption.cpp
    libs/json/sqlite/sqlite3.c
)
target_link_libraries(backend ws2_32)