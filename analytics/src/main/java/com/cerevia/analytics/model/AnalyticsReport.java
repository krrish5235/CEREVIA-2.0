package com.cerevia.analytics.model;

import java.util.List;
import java.util.Map;

public class AnalyticsReport {
    private int overallScore;
    private int totalMoods;
    private int totalJournals;
    private String dominantMood;
    private Map<String, Double> moodDistribution;
    private double averageIntensity;
    private List<String> insights;

    // getters and setters
    public int getOverallScore() { return overallScore; }
    public void setOverallScore(int overallScore) { this.overallScore = overallScore; }
    public int getTotalMoods() { return totalMoods; }
    public void setTotalMoods(int totalMoods) { this.totalMoods = totalMoods; }
    public int getTotalJournals() { return totalJournals; }
    public void setTotalJournals(int totalJournals) { this.totalJournals = totalJournals; }
    public String getDominantMood() { return dominantMood; }
    public void setDominantMood(String dominantMood) { this.dominantMood = dominantMood; }
    public Map<String, Double> getMoodDistribution() { return moodDistribution; }
    public void setMoodDistribution(Map<String, Double> moodDistribution) { this.moodDistribution = moodDistribution; }
    public double getAverageIntensity() { return averageIntensity; }
    public void setAverageIntensity(double averageIntensity) { this.averageIntensity = averageIntensity; }
    public List<String> getInsights() { return insights; }
    public void setInsights(List<String> insights) { this.insights = insights; }
}
