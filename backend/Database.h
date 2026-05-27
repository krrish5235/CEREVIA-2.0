#ifndef DATABASE_H
#define DATABASE_H
#include <string>
#include <sqlite3.h>   
using namespace std;
class Database {
private:
    sqlite3* db;       // Pointer to SQLite database connection
public:
    Database();     // Constructor - Opens the SQLite database and initializes tables if needed
    ~Database();    // Deconstructor - Closes the database connection when the object is destroyed
    sqlite3* getHandle();       // Used by other modules to execute direct SQL queries
    bool checkPIN(const string& pin);     // Checks whether the entered PIN matches the stored PIN
    bool setPIN(const string& pin);      // Updates or sets a new PIN in the database
    string getSecurityQuestion();       // Retrieves the security question stored for the user
    string getEmergencyContact();       // Retrieves the emergency contact number stored in the database
    bool verifySecurityAnswer(const string& answer);       // Verifies whether the entered security answer is correct
};
#endif