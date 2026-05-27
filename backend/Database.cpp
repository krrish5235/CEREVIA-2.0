#include "Database.h"
#include "libs/json/json.hpp"
#include <iostream>
#include <vector>
using json = nlohmann::json;
using namespace std;

// Anonymous namespace used for helper functions that should only
// be accessible inside this file (private utility functions).
namespace
{
    // Executes a SQL command on the database.
    // Used for creating tables or running schema queries.
    // Returns true if the query executes successfully.
    bool runSql(sqlite3 *db, const char *sql)
    {
        char *err = nullptr;
        int rc = sqlite3_exec(db, sql, nullptr, nullptr, &err);
        if (rc != SQLITE_OK)
        {
            cerr << "[DB] SQL error: " << (err ? err : "unknown") << endl;
            sqlite3_free(err);
            return false;
        }
        return true;
    }
    // Ensures that required database tables exist.
    // If tables do not exist, they are automatically created.
    // Also inserts a default user record if none exists.
    void ensureSchema(sqlite3 *db)
    {
        runSql(db,
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "pin TEXT NOT NULL,"
            "security_question TEXT NOT NULL,"
            "security_answer TEXT NOT NULL,"
            "emergency_contact TEXT NOT NULL DEFAULT '112'"
            ");");
        runSql(db,
            "CREATE TABLE IF NOT EXISTS moods ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "mood TEXT NOT NULL,"
            "level INTEGER NOT NULL,"
            "date TEXT NOT NULL"
            ");");
        runSql(db,
            "CREATE TABLE IF NOT EXISTS journals ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "text TEXT NOT NULL,"
            "date TEXT NOT NULL"
            ");");
        runSql(db,
            "INSERT INTO users (id, pin, security_question, security_answer, emergency_contact) "
            "SELECT 1, '1234', 'What is your favorite color?', 'blue', '112' "
            "WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = 1);");
    }
} // creating each and every table for moods, journals, users and handling insertion

// Constructor for Database class.
// Tries to open the SQLite database from multiple possible paths.
// If database opens successfully, it ensures schema exists.
Database::Database() : db(nullptr)
{
    const vector<string> candidates = {
        "../../database/mental_health.db",
        "../database/mental_health.db",
        "database/mental_health.db",
        "mental_health.db"};
    bool opened = false;
    for (const auto &path : candidates)
    {
        cout << "[DB] Opening: " << path << endl;
        if (sqlite3_open(path.c_str(), &db) == SQLITE_OK)
        {
            opened = true;
            break;
        }
        cerr << "[DB] Open failed: " << sqlite3_errmsg(db) << endl;
        sqlite3_close(db);
        db = nullptr;
    }
    if (!opened)
    {
        cerr << "[DB] Unable to open database file from all known paths." << endl;
        return;
    }
    ensureSchema(db);
    cout << "[DB] Connected and schema ready." << endl;
}

// Destructor for Database class.
// Closes the SQLite database connection when program exits.
Database::~Database()
{
    if (db)
    {
        sqlite3_close(db);
    }
}
// Returns the raw SQLite database handle.
// Used by other modules to directly execute SQL queries.
sqlite3 *Database::getHandle()
{
    return db;
}
// Verifies if the entered PIN matches the stored PIN in the database.
// Used during user login authentication.
bool Database::checkPIN(const string &pin)
{
    if (!db)
    {
        return false;
    }
    const char *sql = "SELECT pin FROM users WHERE id = 1";
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK)
    {
        return false;
    }
    bool result = false;
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        const unsigned char *dbPinRaw = sqlite3_column_text(stmt, 0);
        string dbPin = dbPinRaw ? reinterpret_cast<const char *>(dbPinRaw) : "";
        result = (dbPin == pin);
    }
    sqlite3_finalize(stmt);
    return result;
}
// Retrieves the stored emergency contact number from the database
// and returns it in JSON format.
string Database::getEmergencyContact()
{
    const char *sql = "SELECT emergency_contact FROM users WHERE id = 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);

    string contact = "112";
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        const unsigned char *v = sqlite3_column_text(stmt, 0);
        contact = v ? reinterpret_cast<const char *>(v) : "112";
    }
    sqlite3_finalize(stmt);
    json j;
    j["contact"] = contact;
    return j.dump();
}
// Fetches the user's security question from the database
// and returns it as a JSON response.
string Database::getSecurityQuestion()
{
    const char *sql = "SELECT security_question FROM users WHERE id = 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    string q = "Security question not set";
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        const unsigned char *v = sqlite3_column_text(stmt, 0);
        q = v ? reinterpret_cast<const char *>(v) : q;
    }
    sqlite3_finalize(stmt);
    json j;
    j["question"] = q;
    return j.dump();
}
// Checks if the provided security answer matches
// the stored answer in the database.
bool Database::verifySecurityAnswer(const string &answer)
{
    const char *sql = "SELECT security_answer FROM users WHERE id = 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr);
    bool ok = false;
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        const unsigned char *v = sqlite3_column_text(stmt, 0);
        string real = v ? reinterpret_cast<const char *>(v) : "";
        ok = (real == answer);
    }
    sqlite3_finalize(stmt);
    return ok;
}
// Updates the user's PIN in the database.
// Used when registering a new PIN or resetting an existing PIN.
bool Database::setPIN(const string &pin)
{
    if (!db)
    {
        return false;
    }
    const char *sql = "UPDATE users SET pin = ? WHERE id = 1";
    sqlite3_stmt *stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK)
    {
        return false;
    }
    sqlite3_bind_text(stmt, 1, pin.c_str(), -1, SQLITE_TRANSIENT);
    bool success = (sqlite3_step(stmt) == SQLITE_DONE);
    sqlite3_finalize(stmt);
    return success;
}