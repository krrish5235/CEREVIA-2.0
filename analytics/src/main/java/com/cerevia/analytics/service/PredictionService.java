package com.cerevia.analytics.service;

import com.cerevia.analytics.model.MoodEntry;
import com.cerevia.analytics.model.PredictionData;
import com.cerevia.analytics.repository.MoodRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.TextStyle;
import java.util.*;

@Service
public class PredictionService {

    private final MoodRepository repository;

    @Autowired
    public PredictionService(MoodRepository repository) {
        this.repository = repository;
    }

    public PredictionData predictMood() {
        List<MoodEntry> allMoods = repository.findAllMoods();
        
        String today = LocalDate.now().getDayOfWeek().getDisplayName(TextStyle.FULL, Locale.US);
        
        Map<String, Map<String, Long>> moodByDay = new HashMap<>();
        
        for (MoodEntry m : allMoods) {
            if (m.getDate() == null) continue;
            try {
                String dateStr = m.getDate().split("T")[0].split(" ")[0];
                LocalDate d = LocalDate.parse(dateStr);
                String dayName = d.getDayOfWeek().getDisplayName(TextStyle.FULL, Locale.US);
                
                moodByDay.putIfAbsent(dayName, new HashMap<>());
                moodByDay.get(dayName).put(m.getMood(), moodByDay.get(dayName).getOrDefault(m.getMood(), 0L) + 1);
            } catch (Exception e) {
                // ignore unparseable
            }
        }
        
        PredictionData data = new PredictionData();
        data.setDayOfWeek(today);
        
        Map<String, String> pattern = new HashMap<>();
        for (String day : moodByDay.keySet()) {
            String mostCommon = moodByDay.get(day).entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("Neutral");
            pattern.put(day, mostCommon);
        }
        data.setHistoricalPattern(pattern);
        
        Map<String, Long> todaysMoods = moodByDay.getOrDefault(today, new HashMap<>());
        long totalToday = todaysMoods.values().stream().mapToLong(Long::longValue).sum();
        
        if (totalToday > 0) {
            String predicted = todaysMoods.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("Neutral");
            
            double confidence = (double) todaysMoods.get(predicted) / totalToday;
            
            data.setPredictedMood(predicted);
            data.setConfidence(confidence);
            data.setBasedOn(String.format("Based on %d previous %s entries", totalToday, today));
        } else {
            data.setPredictedMood("Neutral");
            data.setConfidence(0.5);
            data.setBasedOn("Not enough data for " + today);
        }
        
        return data;
    }
}
