# AI-Powered Personalized Study Planner

A demo-ready MCA project that creates personalized study schedules using exam urgency, topic difficulty, importance, and current progress.

## Tech Stack
- Frontend: HTML, CSS, JavaScript (no build step)
- Backend: Python Flask
- Database: SQLite
- Charts: Chart.js CDN
- Personalization: Rule-based AI-style planning algorithm

## Run on Windows

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open: http://127.0.0.1:5000

The SQLite database and demo data are created automatically.

## Demo
The app starts with:
- Java
- DBMS
- Artificial Intelligence
- Computer Vision
- Demo topics and progress
- Upcoming exams
- Sample personalized tasks

You can add subjects/topics and generate a fresh plan.

## Project Flow
Student data -> Priority calculation -> Personalized task allocation -> Daily schedule -> Progress tracking -> Analytics

## Priority Algorithm
Priority is increased by:
- Exam urgency
- Topic difficulty
- Importance
- Low completion percentage

The planner allocates the highest-priority unfinished topics first and inserts breaks between study sessions.

## Future Scope
- LLM API integration
- Calendar synchronization
- Mobile app
- Notifications
- Adaptive learning using historical performance


## Deploy online with Render
1. Upload this project to a GitHub repository.
2. In Render, create a new **Web Service** and connect that repository.
3. Set **Root Directory** to `backend`.
4. Set **Build Command** to `pip install -r requirements.txt`.
5. Set **Start Command** to `gunicorn app:app`.
6. Deploy. Render provides a public URL.

Note: the default SQLite database is local to the running instance. For a persistent public deployment, configure a persistent disk or use a managed database. For a quick college demo, seed/demo data can be regenerated on a fresh instance.


## Deploy on Render
1. Push this project to a GitHub repository.
2. In Render, create a new **Web Service** and connect the repository.
3. Build command: `pip install -r backend/requirements.txt`
4. Start command: `cd backend && gunicorn app:app`
5. Select the free instance if available and deploy.

Note: SQLite on a free cloud instance may reset when the service restarts or redeploys. For persistent production data, use a managed PostgreSQL database or persistent disk.

## Updated User Flow
1. Create an account or login.
2. Complete the onboarding profile: course, semester, daily study hours, preferred study time and subjects/exam dates.
3. StudyAI creates a personalized dashboard for that user.
4. Generate a 7-day plan based on exam urgency, difficulty, importance and progress.
5. Data is stored per user in SQLite.
