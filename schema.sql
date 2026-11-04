CREATE DATABASE student_analysis;

USE student_analysis;

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    semester INT
);

CREATE TABLE marks (
    mark_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    subject VARCHAR(50),
    marks INT,
    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
);

CREATE TABLE attendance (
    student_id INT PRIMARY KEY,
    attended INT,
    total INT,
    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
);



INSERT INTO students VALUES
(1, 'Aarav', 3),
(2, 'Priya', 3),
(3, 'Rahul', 3);

INSERT INTO marks (student_id, subject, marks)
VALUES
(1, 'Python', 85),
(1, 'SQL', 90),
(2, 'Python', 92),
(2, 'SQL', 88),
(3, 'Python', 60),
(3, 'SQL', 55);

INSERT INTO attendance VALUES
(1, 45, 50),
(2, 40, 50),
(3, 30, 50);

SELECT * FROM attendance;

SELECT subject,
    ROUND(AVG(marks), 2) AS average_marks
FROM marks
GROUP BY subject;

SELECT
    s.name,
    ROUND(AVG(m.marks), 2) AS average_marks
FROM students s
JOIN marks m
    ON s.student_id = m.student_id
GROUP BY s.student_id, s.name
ORDER BY average_marks DESC;

SELECT
    s.name,
    ROUND(
        100.0 * a.attended / NULLIF(a.total, 0), 2
    ) AS attendance_percentage
FROM students s
JOIN attendance a
    ON s.student_id = a.student_id;