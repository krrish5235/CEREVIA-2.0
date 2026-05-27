#ifndef APISERVER_H     // Prevents this header file from being included multiple times
#define APISERVER_H     // Defines the APISERVER_H macro to mark that this file has been included
// Header file for the API Server class.
// It declares the ApiServer class which is responsible
// for starting and running the backend HTTP server.
class ApiServer {
public:
    // Starts the API server on the given port.
    // This function initializes networking and begins listening
    // for incoming HTTP requests from clients (like a browser or frontend).
    void start(int port);
};
#endif      // Ends the header guard