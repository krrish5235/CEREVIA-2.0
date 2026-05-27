#include "MoodTracker.h"
#include "libs/json/json.hpp"
#include <sqlite3.h>
#include <array>
#include <ctime>
#include <fstream>
#include <random>
#include <sstream>
#include <vector>
using json = nlohmann::json;
using namespace std;
static bool loadJsonFromCandidates(const vector<string> &candidates, json &out)
{
    for (const auto &candidate : candidates)
    {
        ifstream file(candidate);
        if (!file.is_open())
        {
            continue;
        }

        try
        {
            file >> out;
            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    return false;
}

static string normalizeMoodKey(const string &mood)
{
    if (mood == "Happy" || mood == "Sad" || mood == "Angry" || mood == "Anxious" || mood == "Neutral" || mood == "Calm")
    {
        return mood;
    }
    return "Neutral";
}
// Returns a numerical weight for each mood type.
// Positive moods have positive values and negative moods have negative values.
// This weight is used for calculating mental health score.
double getMoodWeight(const string &mood)
{
    if (mood == "Happy")
        return 1.0;
    if (mood == "Calm")
        return 0.8;
    if (mood == "Neutral")
        return 0.5;
    if (mood == "Anxious")
        return -0.6;
    if (mood == "Angry")
        return -0.8;
    if (mood == "Sad")
        return -1.0;
    return 0.0;
}
// Converts mood + level into a mental health score between 0–100.
int computeMentalScore(const string &mood, int level)
{
    double weight = getMoodWeight(mood);
    double raw = (level * weight + 10) * 5;
    if (raw < 0)
        raw = 0;
    if (raw > 100)
        raw = 100;
    return static_cast<int>(raw);
}
// Constructor initializes MoodTracker with database reference
MoodTracker::MoodTracker(Database &db) : db(db) {}
// Adds a new mood entry to the database
void MoodTracker::addMood(const string &body)
{
    json j = json::parse(body);
    string mood = j.value("mood", "");
    int level = j.value("level", 5);
    string date = j.value("date", "Today");
    if (mood.empty())
    {
        return;
    }
    const char *sql = "INSERT INTO moods(mood, level, date) VALUES (?, ?, ?)";
    sqlite3_exec(db.getHandle(), "DELETE FROM moods WHERE id NOT IN (SELECT id FROM moods ORDER BY id DESC LIMIT 7)",
    nullptr, nullptr, nullptr);
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    sqlite3_bind_text(stmt, 1, mood.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 2, level);
    sqlite3_bind_text(stmt, 3, date.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);
}
// Retrieves all stored moods
string MoodTracker::getAllMoods()
{
    json arr = json::array();
    const char *sql = "SELECT mood, level, date FROM moods ORDER BY id DESC";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    while (sqlite3_step(stmt) == SQLITE_ROW)
    {
        json obj;
        obj["mood"] = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
        obj["level"] = sqlite3_column_int(stmt, 1);
        obj["date"] = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 2));
        arr.push_back(obj);
    }
    sqlite3_finalize(stmt);
    return arr.dump();
}
string MoodTracker::getEQResources()
{
    const char *sql = "SELECT mood, level, date FROM moods ORDER BY id DESC LIMIT 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);

    json result;
    result["hasMood"] = false;
    result["latestMood"] = "Neutral";
    result["displayMood"] = "Neutral";
    result["level"] = nullptr;
    result["date"] = nullptr;

    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        const unsigned char *moodText = sqlite3_column_text(stmt, 0);
        const unsigned char *dateText = sqlite3_column_text(stmt, 2);
        const string displayMood = moodText ? reinterpret_cast<const char *>(moodText) : "Neutral";
        result["hasMood"] = true;
        result["displayMood"] = displayMood;
        result["latestMood"] = normalizeMoodKey(displayMood);
        result["level"] = sqlite3_column_int(stmt, 1);
        result["date"] = dateText ? reinterpret_cast<const char *>(dateText) : "";
    }
    sqlite3_finalize(stmt);

    json data;
    const vector<string> candidates = {
        "eq_resources.json",
        "backend/eq_resources.json",
        "../eq_resources.json",
        "../backend/eq_resources.json",
        "../../eq_resources.json",
        "../../backend/eq_resources.json"
    };

    if (!loadJsonFromCandidates(candidates, data) || !data.is_object())
    {
        result["error"] = "EQ resources file not found or invalid.";
        result["resources"] = {
            {"articles", json::array()},
            {"videos", json::array()},
            {"activities", json::array()},
            {"songs", json::array()}
        };
        return result.dump();
    }

    const string moodKey = normalizeMoodKey(result["latestMood"].get<string>());
    result["latestMood"] = moodKey;
    if (data.contains(moodKey) && data[moodKey].is_object())
    {
        result["resources"] = data[moodKey];
    }
    else
    {
        result["resources"] = data.value("Neutral", json::object());
    }

    return result.dump();
}
// Detects crisis if last 3 moods are Sad or Angry
string MoodTracker::checkCrisisStatus()
{
    const char *sql = "SELECT mood FROM moods ORDER BY id DESC LIMIT 3";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    int count = 0;
    bool allSadOrAngry = true;
    while (sqlite3_step(stmt) == SQLITE_ROW)
    {
        string mood = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
        count++;
        if (!(mood == "Sad" || mood == "Angry"))
        {
            allSadOrAngry = false;
        }
    }
    sqlite3_finalize(stmt);
    const bool crisis = (count == 3 && allSadOrAngry);
    string contact = "112";
    const char *contactSql = "SELECT emergency_contact FROM users WHERE id = 1";
    sqlite3_stmt *contactStmt = nullptr;
    if (sqlite3_prepare_v2(db.getHandle(), contactSql, -1, &contactStmt, nullptr) == SQLITE_OK)
    {
        if (sqlite3_step(contactStmt) == SQLITE_ROW)
        {
            const unsigned char *v = sqlite3_column_text(contactStmt, 0);
            if (v)
            {
                contact = reinterpret_cast<const char *>(v);
            }
        }
    }
    sqlite3_finalize(contactStmt);
    json j;
    j["crisis"] = crisis;
    j["contact"] = contact;
    if (crisis)
    {
        j["message"] = "Crisis detected: 3 consecutive Sad/Angry moods logged. Please contact a doctor now at " + contact + ".";
    }
    else
    {
        j["message"] = "Crisis settled: your latest mood pattern is no longer a Sad/Angry streak.";
    }
    return j.dump();
}
// Returns last 7 moods for weekly visualization
string MoodTracker::getWeeklyStats()
{
    json arr = json::array();
    const char *sql = "SELECT mood, level FROM moods ORDER BY id DESC LIMIT 7";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    int idx = 1;
    while (sqlite3_step(stmt) == SQLITE_ROW)
    {
        json obj;
        string mood = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
        int level = sqlite3_column_int(stmt, 1);
        obj["label"] = "D" + to_string(idx);
        obj["mood"] = mood;
        obj["level"] = level;
        arr.push_back(obj);
        idx++;
    }
    sqlite3_finalize(stmt);
    return arr.dump();
}
// Returns a suggestion based on the latest mood
string MoodTracker::getSuggestion()
{
    const char *sql = "SELECT mood FROM moods ORDER BY id DESC LIMIT 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    string mood = "Neutral";
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        mood = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
    }
    sqlite3_finalize(stmt);
    const char *crisisSql = "SELECT mood FROM moods ORDER BY id DESC LIMIT 3";
    sqlite3_stmt *crisisStmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), crisisSql, -1, &crisisStmt, nullptr);
    int crisisCount = 0;
    bool allSadOrAngry = true;
    while (sqlite3_step(crisisStmt) == SQLITE_ROW)
    {
        string recentMood = reinterpret_cast<const char *>(sqlite3_column_text(crisisStmt, 0));
        crisisCount++;
        if (!(recentMood == "Sad" || recentMood == "Angry"))
        {
            allSadOrAngry = false;
        }
    }
    sqlite3_finalize(crisisStmt);
    if (crisisCount == 3 && allSadOrAngry)
    {
        string contact = "112";
        const char *contactSql = "SELECT emergency_contact FROM users WHERE id = 1";
        sqlite3_stmt *contactStmt = nullptr;
        if (sqlite3_prepare_v2(db.getHandle(), contactSql, -1, &contactStmt, nullptr) == SQLITE_OK)
        {
            if (sqlite3_step(contactStmt) == SQLITE_ROW)
            {
                const unsigned char *v = sqlite3_column_text(contactStmt, 0);
                if (v)
                {
                    contact = reinterpret_cast<const char *>(v);
                }
            }
        }
        sqlite3_finalize(contactStmt);
        json crisisResult;
        crisisResult["mood"] = mood;
        crisisResult["message"] = "Crisis alert: Please contact a doctor now at " + contact + ".";
        return crisisResult.dump();
    }
    json suggestions;
    try
    {
        ifstream file("suggestion.json");
        if (!file.is_open())
            file.open("../suggestion.json");
        if (!file.is_open())
            file.open("../../suggestion.json");
        if (!file.is_open())
            file.open("backend/suggestion.json");
        if (!file.is_open())
        {
            json err;
            err["message"] = "Suggestion file not found.";
            return err.dump();
        }
        file >> suggestions;
        file.close();
    }
    catch (...)
    {
        json err;
        err["message"] = "Error reading suggestion file.";
        return err.dump();
    }
    string message = "Take care of yourself today.";
    if (suggestions.contains(mood))
    {
        auto moodSuggestions = suggestions[mood];
        if (moodSuggestions.is_array() && !moodSuggestions.empty())
        {
            int index = rand() % moodSuggestions.size();
            message = moodSuggestions[index];
        }
    }
    json result;
    result["mood"] = mood;
    result["message"] = message;
    return result.dump();
}
// Calculates overall mental health percentage
string MoodTracker::getAverageMoodPercent()
{
    const char *sql = "SELECT mood, level FROM moods";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    double total = 0;
    int count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW)
    {
        string mood = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
        int level = sqlite3_column_int(stmt, 1);
        int score = computeMentalScore(mood, level);
        total += score;
        count++;
    }
    sqlite3_finalize(stmt);
    int avg = (count == 0) ? 0 : static_cast<int>(total / count);
    json j;
    j["percent"] = avg;
    return j.dump();
}
// Returns the most frequently logged mood
string MoodTracker::getFrequentMood()
{
    json out;
    out["mood"] = "";
    const char *sql = "SELECT mood, COUNT(*) as c FROM moods GROUP BY mood ORDER BY c DESC LIMIT 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        out["mood"] = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
    }
    sqlite3_finalize(stmt);
    return out.dump();
}
// Returns the most recent mood entry
string MoodTracker::getLatestMood()
{
    json out;
    out["mood"] = "";
    const char *sql = "SELECT mood FROM moods ORDER BY id DESC LIMIT 1";
    sqlite3_stmt *stmt = nullptr;
    sqlite3_prepare_v2(db.getHandle(), sql, -1, &stmt, nullptr);
    if (sqlite3_step(stmt) == SQLITE_ROW)
    {
        out["mood"] = reinterpret_cast<const char *>(sqlite3_column_text(stmt, 0));
    }
    sqlite3_finalize(stmt);
    return out.dump();
}
