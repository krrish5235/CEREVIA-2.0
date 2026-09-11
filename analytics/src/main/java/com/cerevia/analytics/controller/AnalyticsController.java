package com.cerevia.analytics.controller;

import com.cerevia.analytics.model.*;
import com.cerevia.analytics.service.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/analytics")
@CrossOrigin(origins = "*")
public class AnalyticsController {

    private final MoodAnalyticsService analyticsService;
    private final PredictionService predictionService;
    private final StreakService streakService;

    @Autowired
    public AnalyticsController(MoodAnalyticsService analyticsService,
                               PredictionService predictionService,
                               StreakService streakService) {
        this.analyticsService = analyticsService;
        this.predictionService = predictionService;
        this.streakService = streakService;
    }

    @GetMapping("/trends")
    public ResponseEntity<?> getTrends() {
        try {
            return ResponseEntity.ok(analyticsService.getTrends(30));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/weekly-report")
    public ResponseEntity<?> getWeeklyReport() {
        try {
            return ResponseEntity.ok(analyticsService.getSummaryReport());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/predict")
    public ResponseEntity<?> predictMood() {
        try {
            return ResponseEntity.ok(predictionService.predictMood());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/streaks")
    public ResponseEntity<?> getStreaks() {
        try {
            return ResponseEntity.ok(streakService.getStreaks());
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/summary")
    public ResponseEntity<?> getSummary() {
        try {
            Map<String, Object> summary = new HashMap<>();
            summary.put("report", analyticsService.getSummaryReport());
            summary.put("streaks", streakService.getStreaks());
            summary.put("prediction", predictionService.predictMood());
            return ResponseEntity.ok(summary);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/export")
    public ResponseEntity<?> exportData() {
        try {
            Map<String, Object> summary = new HashMap<>();
            summary.put("report", analyticsService.getSummaryReport());
            summary.put("streaks", streakService.getStreaks());
            summary.put("prediction", predictionService.predictMood());
            
            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"analytics-export.json\"")
                .body(summary);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of("error", e.getMessage()));
        }
    }
}
