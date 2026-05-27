#ifndef MOODTRACKER_H
#define MOODTRACKER_H
#include<string>
#include "Database.h"
using namespace std;
class MoodTracker {
private:
    // Reference to the Database object.
    // This allows the MoodTracker class to read and store mood data.
    Database &db;
public:
    // Constructor that initializes MoodTracker with a database reference
    // so mood data can be stored and retrieved.
    MoodTracker(Database &d);
    void addMood(const string& body);       // Adds a new mood entry to the database.
    string getAllMoods();       // Retrieves all mood entries stored in the database.
    // Dashboard stats
    string getWeeklyStats();    // Returns the last 7 mood entries for weekly analysis.
    string getSuggestion();     // Provides a suggestion based on the user's latest mood.
    string getAverageMoodPercent();  // { "percent": 72 }
    string getFrequentMood();        // { "mood": "Happy" }
    string getEQResources();
    string getLatestMood();          // { "mood": "Sad" }
    string checkCrisisStatus();     // Detects a crisis situation if the last three moods
};  
#endif