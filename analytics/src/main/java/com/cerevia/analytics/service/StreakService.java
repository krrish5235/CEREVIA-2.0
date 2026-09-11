package com.cerevia.analytics.service;

import com.cerevia.analytics.model.MoodEntry;
import com.cerevia.analytics.model.StreakData;
import com.cerevia.analytics.repository.MoodRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
public class StreakService {

    private final MoodRepository repository;

    @Autowired
    public StreakService(MoodRepository repository) {
        this.repository = repository;
    }

    public StreakData getStreaks() {
        StreakData data = new StreakData();
        List<MoodEntry> moods = repository.findAllMoods(); 
        
        int currentStreak = 0;
        int maxStreak = 0;
        int tempMax = 0;
        
        for (MoodEntry m : moods) {
            String mo = m.getMood().toLowerCase();
            if (mo.equals("happy") || mo.equals("calm") || mo.equals("neutral")) {
                tempMax++;
                if (maxStreak == 0 || tempMax > maxStreak) {
                    maxStreak = tempMax;
                }
            } else {
                tempMax = 0;
            }
        }
        
        for (MoodEntry m : moods) {
            String mo = m.getMood().toLowerCase();
            if (mo.equals("happy") || mo.equals("calm") || mo.equals("neutral")) {
                currentStreak++;
            } else {
                break;
            }
        }
        
        data.setCurrentPositiveStreak(currentStreak);
        data.setLongestPositiveStreak(maxStreak);
        
        List<String> jDates = repository.getJournalDates();
        Set<String> uniqueDates = jDates.stream()
            .map(d -> d.split("T")[0].split(" ")[0])
            .collect(Collectors.toSet());
        
        int journalStreak = calculateConsecutiveDays(jDates);
        data.setJournalStreak(journalStreak);
        
        Set<String> allActive = moods.stream()
            .map(m -> m.getDate().split("T")[0].split(" ")[0])
            .collect(Collectors.toSet());
        allActive.addAll(uniqueDates);
        
        data.setTotalActiveDays(allActive.size());
        
        if (!moods.isEmpty()) {
            data.setLastLogDate(moods.get(0).getDate());
        } else if (!jDates.isEmpty()) {
            data.setLastLogDate(jDates.get(0));
        }
        
        return data;
    }
    
    private int calculateConsecutiveDays(List<String> datesDesc) {
        if (datesDesc == null || datesDesc.isEmpty()) return 0;
        
        List<LocalDate> parsed = datesDesc.stream()
            .map(d -> {
                try {
                    return LocalDate.parse(d.split("T")[0].split(" ")[0]);
                } catch (Exception e) { return null; }
            })
            .filter(d -> d != null)
            .distinct()
            .sorted((a, b) -> b.compareTo(a))
            .collect(Collectors.toList());
            
        if (parsed.isEmpty()) return 0;
        
        int streak = 1;
        LocalDate current = parsed.get(0);
        
        for (int i = 1; i < parsed.size(); i++) {
            if (ChronoUnit.DAYS.between(parsed.get(i), current) == 1) {
                streak++;
                current = parsed.get(i);
            } else {
                break;
            }
        }
        return streak;
    }
}
