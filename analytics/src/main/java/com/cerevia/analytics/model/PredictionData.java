package com.cerevia.analytics.model;

import java.util.Map;

public class PredictionData {
    private String predictedMood;
    private double confidence;
    private String dayOfWeek;
    private String basedOn;
    private Map<String, String> historicalPattern;

    public String getPredictedMood() { return predictedMood; }
    public void setPredictedMood(String predictedMood) { this.predictedMood = predictedMood; }
    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }
    public String getDayOfWeek() { return dayOfWeek; }
    public void setDayOfWeek(String dayOfWeek) { this.dayOfWeek = dayOfWeek; }
    public String getBasedOn() { return basedOn; }
    public void setBasedOn(String basedOn) { this.basedOn = basedOn; }
    public Map<String, String> getHistoricalPattern() { return historicalPattern; }
    public void setHistoricalPattern(Map<String, String> historicalPattern) { this.historicalPattern = historicalPattern; }
}
