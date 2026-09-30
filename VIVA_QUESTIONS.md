# Viva Questions — AI-Powered Personalized Study Planner

1. What is the project?
It is a web application that generates a personalized study plan according to a student's subjects, exam dates, topic difficulty, importance and progress.

2. Why is personalization needed?
Different students have different weak areas, available hours and exam priorities. A fixed timetable cannot handle these differences.

3. How does the planner work?
It collects student data, calculates priority scores, ranks unfinished topics and allocates them into available study sessions.

4. What factors affect priority?
Exam urgency, difficulty, importance and low progress.

5. What is the formula?
Priority Score = Urgency + Difficulty + Importance + Low Progress Factor.

6. Why Flask?
Flask is lightweight, simple and suitable for creating REST APIs quickly.

7. Why SQLite?
SQLite is easy to deploy, requires no separate database server and is suitable for a student project.

8. What is REST API?
A REST API allows the frontend and backend to communicate through HTTP requests such as GET, POST, PUT and DELETE.

9. What is CRUD?
Create, Read, Update and Delete are the four basic database operations.

10. What is React?
This version intentionally uses lightweight HTML/CSS/JavaScript to make deployment simple. The architecture can be migrated to React later.

11. Where is AI used?
The personalization engine behaves as an intelligent planning layer by ranking study topics from multiple student-specific inputs. An LLM can be connected as a future enhancement.

12. How is exam urgency calculated?
Topics belonging to exams with fewer remaining days receive a higher urgency score.

13. How are weak topics detected?
Topics with lower completion percentages receive a larger low-progress factor, especially when combined with high difficulty and importance.

14. What happens when a topic is completed?
Its progress becomes 100% and the planner excludes it from future generated plans.

15. What is the benefit of analytics?
Analytics helps the student understand subject progress and completed/pending tasks.

16. What is the database relationship?
A subject can contain many topics. Generated tasks reference topics and store schedule information.

17. What is the future scope?
LLM integration, notifications, Google Calendar integration, mobile app and adaptive learning.

18. What are limitations?
The current planner is rule-based and does not yet learn from long-term student behavior.

19. How can it be made more intelligent?
Historical performance can be stored and used with machine learning to predict required study time.

20. What is the main objective?
To turn student-specific academic information into an actionable and prioritized study schedule.
