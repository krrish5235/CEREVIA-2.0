package com.cerevia.analytics.service;

import com.cerevia.analytics.model.AnalyticsReport;
import com.cerevia.analytics.model.MoodEntry;
import com.cerevia.analytics.model.TrendData;
import com.cerevia.analytics.repository.MoodRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class MoodAnalyticsService {

    private final MoodRepository repository;

    @Autowired
    public MoodAnalyticsService(MoodRepository repository) {
        this.repository = repository;
    }

    public TrendData getTrends(int days) {
        List<MoodEntry> recentMoods = repository.findRecentMoods(days);
        Collections.reverse(recentMoods); // Oldest to newest for trend
        
        List<String> labels = new ArrayList<>();
        List<Integer> values = new ArrayList<>();
        List<String> moods = new ArrayList<>();
        List<Double> movingAverage = new ArrayList<>();
        
        for (int i = 0; i < recentMoods.size(); i++) {
            MoodEntry entry = recentMoods.get(i);
            labels.add(entry.getDate());
            values.add(entry.getLevel());
            moods.add(entry.getMood());
            
            // 3-day moving average
            double sum = 0;
            int count = 0;
            for (int j = Math.max(0, i - 2); j <= i; j++) {
                sum += recentMoods.get(j).getLevel();
                count++;
            }
            movingAverage.add(sum / count);
        }
        
        String trend = "stable";
        if (values.size() >= 4) {
            int mid = values.size() / 2;
            double firstHalfAvg = values.subList(0, mid).stream().mapToInt(Integer::intValue).average().orElse(0);
            double secondHalfAvg = values.subList(mid, values.size()).stream().mapToInt(Integer::intValue).average().orElse(0);
            if (secondHalfAvg > firstHalfAvg + 0.5) trend = "improving";
            else if (secondHalfAvg < firstHalfAvg - 0.5) trend = "declining";
        }
        
        TrendData trendData = new TrendData();
        trendData.setLabels(labels);
        trendData.setValues(values);
        trendData.setMoods(moods);
        trendData.setMovingAverage(movingAverage);
        trendData.setTrend(trend);
        return trendData;
    }

    public AnalyticsReport getSummaryReport() {
        AnalyticsReport report = new AnalyticsReport();
        List<MoodEntry> allMoods = repository.findAllMoods();
        report.setTotalMoods(allMoods.size());
        report.setTotalJournals(repository.countJournals());
        
        Map<String, Double> dist = repository.findMoodDistribution();
        report.setMoodDistribution(dist);
        
        String dominant = dist.entrySet().stream()
            .max(Map.Entry.comparingByValue())
            .map(Map.Entry::getKey)
            .orElse("None");
        report.setDominantMood(dominant);
        
        double avgIntensity = allMoods.stream().mapToInt(MoodEntry::getLevel).average().orElse(0.0);
        report.setAverageIntensity(avgIntensity);
        
        double totalScore = 0;
        for (MoodEntry m : allMoods) {
            int weight = getMoodWeight(m.getMood());
            totalScore += weight * (m.getLevel() / 10.0);
        }
        int overallScore = allMoods.isEmpty() ? 0 : (int) (totalScore / allMoods.size());
        report.setOverallScore(overallScore);
        
        List<String> insights = new ArrayList<>();
        if (!dist.isEmpty()) {
            insights.add(String.format("Your most common mood is %s (%.1f%%)", dominant, dist.getOrDefault(dominant, 0.0)));
        }
        TrendData trends = getTrends(7);
        insights.add("Your mood has been " + trends.getTrend() + " this week.");
        report.setInsights(insights);
        
        return report;
    }
    
    private int getMoodWeight(String mood) {
        if (mood == null) return 50;
        switch(mood.toLowerCase()) {
            case "happy": return 90;
            case "calm": return 80;
            case "neutral": return 60;
            case "anxious": return 35;
            case "sad": return 25;
            case "angry": return 20;
            default: return 50;
        }
    }
}
