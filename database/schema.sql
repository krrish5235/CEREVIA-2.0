CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pin TEXT NOT NULL,
    security_question TEXT NOT NULL,
    security_answer TEXT NOT NULL
);

INSERT INTO users (pin, security_question, security_answer)
VALUES ('1234', 'What is your favorite color?', 'blue');


CREATE TABLE moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mood TEXT NOT NULL,
    level INTEGER NOT NULL,
    date TEXT NOT NULL
);


CREATE TABLE journals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    date TEXT NOT NULL
);


CREATE VIEW frequent_mood AS
SELECT mood, COUNT(*) AS count
FROM moods
GROUP BY mood
ORDER BY count DESC
LIMIT 1;


CREATE VIEW latest_mood AS
SELECT mood, date
FROM moods
ORDER BY id DESC
LIMIT 1;


CREATE VIEW average_mood AS
SELECT AVG(level) AS avg_level
FROM moods;