# AI-Powered Personalized Study Planner

## 1. Introduction
The AI-Powered Personalized Study Planner is a web application designed to help students organize academic preparation according to their individual needs. It considers examination deadlines, topic difficulty, importance, and current progress to generate a personalized study schedule.

## 2. Problem Statement
Students often create fixed study timetables without considering changing exam priorities, weak topics, or available study time. This can lead to inefficient preparation and missed revision opportunities.

## 3. Proposed System
The proposed system collects student academic information and applies a personalization algorithm to rank unfinished topics. High-priority topics are allocated earlier in the schedule, while completed topics are excluded.

## 4. Objectives
- Generate personalized study plans.
- Prioritize weak and difficult topics.
- Consider exam urgency.
- Track study progress.
- Provide analytics and visual feedback.
- Allow students to update their plan.

## 5. Modules
1. Dashboard
2. Subject Management
3. Topic Management
4. Study Preferences
5. Personalized Plan Generator
6. Task Tracking
7. Analytics

## 6. AI Personalization
The planner calculates a priority score from exam urgency, difficulty, importance, and low progress. This is a deterministic intelligent-planning layer and can be extended with an LLM API for natural-language recommendations.

## 7. Algorithm
Priority Score = Urgency + Difficulty + Importance + Low Progress Factor.

Exam urgency is higher when fewer days remain. Hard topics receive a higher difficulty score. High-importance topics receive a higher importance score. Topics with lower completion receive a higher low-progress score.

## 8. Technology
Frontend: HTML, CSS, JavaScript, Chart.js.
Backend: Python Flask.
Database: SQLite.

## 9. Database
Subjects store exam and progress information. Topics belong to subjects. Preferences store daily study constraints. Tasks store generated schedule entries.

## 10. Future Scope
LLM integration, notifications, calendar synchronization, mobile application, adaptive learning, and performance prediction.

## 11. Conclusion
The project demonstrates how personalized academic data can be transformed into an actionable study schedule. It provides a practical foundation for intelligent educational planning.
