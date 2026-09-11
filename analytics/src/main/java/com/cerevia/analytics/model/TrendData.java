package com.cerevia.analytics.model;

import java.util.List;

public class TrendData {
    private List<String> labels;
    private List<Integer> values;
    private List<String> moods;
    private List<Double> movingAverage;
    private String trend;

    public List<String> getLabels() { return labels; }
    public void setLabels(List<String> labels) { this.labels = labels; }
    public List<Integer> getValues() { return values; }
    public void setValues(List<Integer> values) { this.values = values; }
    public List<String> getMoods() { return moods; }
    public void setMoods(List<String> moods) { this.moods = moods; }
    public List<Double> getMovingAverage() { return movingAverage; }
    public void setMovingAverage(List<Double> movingAverage) { this.movingAverage = movingAverage; }
    public String getTrend() { return trend; }
    public void setTrend(String trend) { this.trend = trend; }
}
