package com.cerevia.analytics.model;

public class StreakData {
    private int currentPositiveStreak;
    private int longestPositiveStreak;
    private int journalStreak;
    private int totalActiveDays;
    private String lastLogDate;

    public int getCurrentPositiveStreak() { return currentPositiveStreak; }
    public void setCurrentPositiveStreak(int currentPositiveStreak) { this.currentPositiveStreak = currentPositiveStreak; }
    public int getLongestPositiveStreak() { return longestPositiveStreak; }
    public void setLongestPositiveStreak(int longestPositiveStreak) { this.longestPositiveStreak = longestPositiveStreak; }
    public int getJournalStreak() { return journalStreak; }
    public void setJournalStreak(int journalStreak) { this.journalStreak = journalStreak; }
    public int getTotalActiveDays() { return totalActiveDays; }
    public void setTotalActiveDays(int totalActiveDays) { this.totalActiveDays = totalActiveDays; }
    public String getLastLogDate() { return lastLogDate; }
    public void setLastLogDate(String lastLogDate) { this.lastLogDate = lastLogDate; }
}
