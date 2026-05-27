#include "JournalManager.h"
#include "libs/json/json.hpp"
#include "Encryption.h"     // Used to encrypt journal and make it secure
#include <sqlite3.h>
#include <ctime>        // Used for generating timestamps
using json = nlohmann::json;
using namespace std;

// Constructor for JournalManager.
// Receives a reference to the Database object so this class
// can execute SQL queries on the application's database.
JournalManager::JournalManager(Database& db) : db(db) {}
// Adds a new journal entry into the database.
// The text is first encrypted before storing.
// Uses prepared SQL statements for safe insertion.
void JournalManager::addEntry(const string &body) {
    json j = json::parse(body);
    string text = j.value("text", "");
    // Parse JSON request body and extract journal text
    if (text.empty()) {
        return;
    }   // donot store any empty journal
    // Encrypt before saving
    string encText = Encryption::encrypt(text, key);
    time_t now = time(0);
    string date = ctime(&now);
    if (!date.empty()) date.pop_back();
    const char* sql = "INSERT INTO journals(text, date) VALUES (?, ?)";
    // Keep only last 7 journal entries
    sqlite3_exec(db.getHandle(),
    "DELETE FROM journals WHERE id NOT IN (SELECT id FROM journals ORDER BY id DESC LIMIT 7)", nullptr, nullptr, nullptr);
    sqlite3_stmt* stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    // Bind encrypted text and date values to SQL placeholders
    sqlite3_bind_text(stmt, 1, encText.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, date.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);
}
// Retrieves all journal entries from the database.
// Decrypts each journal text before returning it as JSON.
string JournalManager::getAll() {
    json arr = json::array();
    const char* sql = "SELECT date, text FROM journals ORDER BY id DESC";
    sqlite3_stmt* stmt = nullptr;
    if (sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr) == SQLITE_OK) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            const unsigned char* d = sqlite3_column_text(stmt, 0);
            const unsigned char* t = sqlite3_column_text(stmt, 1);
            string date = d ? reinterpret_cast<const char*>(d) : "";
            string encText = t ? reinterpret_cast<const char*>(t) : "";
            string decText = Encryption::decrypt(encText, key);
            json obj;
            obj["date"] = date;
            obj["text"] = decText;
            arr.push_back(obj);
        }
    }
    sqlite3_finalize(stmt);
    return arr.dump();
}
// Returns the total number of journal entries stored in the database as JSON.
string JournalManager::getCountJSON() {
    int count = 0;
    const char* sql = "SELECT COUNT(*) FROM journals";
    sqlite3_stmt* stmt = nullptr;
    if (sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr) == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            count = sqlite3_column_int(stmt, 0);
        }
    }
    sqlite3_finalize(stmt);
    json j;
    j["count"] = count;
    return j.dump();
}
