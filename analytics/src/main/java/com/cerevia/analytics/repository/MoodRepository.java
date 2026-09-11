package com.cerevia.analytics.repository;

import com.cerevia.analytics.model.MoodEntry;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.sql.ResultSet;

@Repository
public class MoodRepository {

    private final JdbcTemplate jdbcTemplate;

    @Autowired
    public MoodRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<MoodEntry> findAllMoods() {
        return jdbcTemplate.query(
            "SELECT * FROM moods ORDER BY id DESC",
            (rs, rowNum) -> mapRowToMoodEntry(rs)
        );
    }

    public List<MoodEntry> findRecentMoods(int limit) {
        return jdbcTemplate.query(
            "SELECT * FROM moods ORDER BY id DESC LIMIT ?",
            (rs, rowNum) -> mapRowToMoodEntry(rs),
            limit
        );
    }

    public int countMoods() {
        Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM moods", Integer.class);
        return count != null ? count : 0;
    }

    public int countJournals() {
        Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM journals", Integer.class);
        return count != null ? count : 0;
    }

    public Map<String, Double> findMoodDistribution() {
        int total = countMoods();
        if (total == 0) return new HashMap<>();

        List<Map<String, Object>> rows = jdbcTemplate.queryForList(
            "SELECT mood, COUNT(*) as count FROM moods GROUP BY mood"
        );

        Map<String, Double> distribution = new HashMap<>();
        for (Map<String, Object> row : rows) {
            String mood = (String) row.get("mood");
            int count = ((Number) row.get("count")).intValue();
            distribution.put(mood, (count * 100.0) / total);
        }
        return distribution;
    }

    public List<MoodEntry> findMoodsByDayOfWeek(String day) {
        return findAllMoods();
    }

    public List<String> getJournalDates() {
        return jdbcTemplate.query(
            "SELECT DISTINCT date FROM journals ORDER BY date DESC",
            (rs, rowNum) -> rs.getString("date")
        );
    }
    
    public List<String> getMoodDates() {
        return jdbcTemplate.query(
            "SELECT DISTINCT date FROM moods ORDER BY date DESC",
            (rs, rowNum) -> rs.getString("date")
        );
    }

    private MoodEntry mapRowToMoodEntry(ResultSet rs) throws java.sql.SQLException {
        return new MoodEntry(
            rs.getInt("id"),
            rs.getString("mood"),
            rs.getInt("level"),
            rs.getString("date")
        );
    }
}
