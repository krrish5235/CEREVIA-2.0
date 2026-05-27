#ifndef JOURNALMANAGER_H
#define JOURNALMANAGER_H
#include <string>
#include "Database.h"
using namespace std;
class JournalManager {
private:
    // Reference to the Database object.
    // This allows JournalManager to execute SQL queries.
    Database& db;
    // Encryption key used for encrypting and decrypting journal text.
    // This key is used by the Encryption class.
    string key = "secret";   // encryption key
public:
    // Constructor that receives the Database object
    // so journal operations can interact with the database.
    JournalManager(Database& db);
    // Adds a new journal entry to the database.
    // The entry is received as JSON, encrypted, and then stored.
    void addEntry(const string& body);
    // Retrieves all stored journal entries.
    // The stored encrypted text is decrypted before returning.
    string getAll();
    // Returns the total number of journal entries in JSON format.
    string getCountJSON();
};
#endif