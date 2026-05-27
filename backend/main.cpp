// This is the entry point of the backend application.
// It starts the API server which listens for client requests.
#include "ApiServer.h"
using namespace std;
int main() {
    ApiServer api;      // Create an object of ApiServer class
    api.start(5000);    // Start the API server on port 5000
    return 0;
}