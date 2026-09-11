package com.cerevia.analytics.model;

public class MoodEntry {
    private int id;
    private String mood;
    private int level;
    private String date;

    public MoodEntry() {}

    public MoodEntry(int id, String mood, int level, String date) {
        this.id = id;
        this.mood = mood;
        this.level = level;
        this.date = date;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public String getMood() { return mood; }
    public void setMood(String mood) { this.mood = mood; }
    public int getLevel() { return level; }
    public void setLevel(int level) { this.level = level; }
    public String getDate() { return date; }
    public void setDate(String date) { this.date = date; }
}
