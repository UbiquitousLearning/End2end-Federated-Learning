cmake_minimum_required(VERSION 3.4.1)

set(lib_DIR ${CMAKE_SOURCE_DIR}/libs)
include_directories(${CMAKE_SOURCE_DIR}/includes)

add_library( MNN SHARED IMPORTED )
set_target_properties(
        MNN
        PROPERTIES IMPORTED_LOCATION
        ${lib_DIR}/${ANDROID_ABI}/libMNN.so
)

add_library( MNNTrain SHARED IMPORTED )
set_target_properties(
        MNNTrain
        PROPERTIES IMPORTED_LOCATION
        ${lib_DIR}/${ANDROID_ABI}/libMNNTrain.so
)

add_library( MNN_Express SHARED IMPORTED )
set_target_properties(
        MNN_Express
        PROPERTIES IMPORTED_LOCATION
        ${lib_DIR}/${ANDROID_ABI}/libMNN_Express.so
)

#file(GLOB_RECURSE CPP_SRCS src/main/jni/*.cpp)
file(GLOB_RECURSE CPP_SRCS src/main/jni/mnndatanative.cpp)
add_library( mnncore SHARED ${CPP_SRCS} )

find_library( log-lib log )
find_library( jnigraphics-lib jnigraphics )

add_definitions(-DMNN_USE_LOGCAT)
target_link_libraries( mnncore MNN ${log-lib} ${jnigraphics-lib})
target_link_libraries( mnncore MNNTrain ${log-lib} ${jnigraphics-lib})
target_link_libraries( mnncore MNN_Express ${log-lib} ${jnigraphics-lib})