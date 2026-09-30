from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3, os, secrets
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "study_planner.db"
FRONTEND = BASE.parent / "frontend"
app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
CORS(app)

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        course TEXT DEFAULT 'MCA',
        semester TEXT DEFAULT 'Current Semester',
        profile_completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS sessions(
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Medium',
        priority TEXT DEFAULT 'Medium',
        progress INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS topics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Medium',
        importance TEXT DEFAULT 'Medium',
        progress INTEGER DEFAULT 0,
        estimated_minutes INTEGER DEFAULT 60,
        status TEXT DEFAULT 'Not Started',
        FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS preferences(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        daily_hours REAL DEFAULT 4,
        study_time TEXT DEFAULT 'Evening',
        session_minutes INTEGER DEFAULT 60,
        break_minutes INTEGER DEFAULT 15,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic_id INTEGER,
        subject TEXT,
        topic TEXT,
        task_date TEXT,
        start_time TEXT,
        duration INTEGER,
        status TEXT DEFAULT 'Pending',
        priority_score REAL DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    conn.commit(); conn.close()

def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): return None
    token = auth.split(" ", 1)[1].strip()
    conn = db(); row = conn.execute("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?", (token,)).fetchone(); conn.close()
    return dict(row) if row else None

def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user: return jsonify({"error":"Authentication required"}), 401
        request.user = user
        return fn(*args, **kwargs)
    return wrapper

def priority_score(topic, subject):
    today=date.today()
    try: days=max(1,(datetime.strptime(subject["exam_date"], "%Y-%m-%d").date()-today).days)
    except: days=30
    urgency=40 if days<=3 else 30 if days<=7 else 20 if days<=14 else 10
    diff={"Easy":5,"Medium":10,"Hard":15}.get(topic["difficulty"],10)
    imp={"Low":5,"Medium":10,"High":15}.get(topic["importance"],10)
    low=max(0,20-topic["progress"]//5)
    return urgency+diff+imp+low

def create_subjects(conn, user_id, items):
    for s in items:
        cur=conn.execute("INSERT INTO subjects(user_id,name,exam_date,difficulty,priority,progress) VALUES(?,?,?,?,?,?)",
            (user_id,s["name"],s["exam_date"],s.get("difficulty","Medium"),s.get("priority","Medium"),int(s.get("progress",0))))
        sid=cur.lastrowid
        topics=s.get("topics") or [s["name"]+" Fundamentals", s["name"]+" Important Questions", s["name"]+" Revision"]
        for i,t in enumerate(topics):
            conn.execute("INSERT INTO topics(subject_id,name,difficulty,importance,progress,estimated_minutes) VALUES(?,?,?,?,?,?)",
                (sid,t,"Hard" if i==0 else "Medium","High" if i<2 else "Medium",0,60 if i else 90))

@app.route("/")
def index(): return send_from_directory(FRONTEND,"index.html")
@app.route("/<path:path>")
def static_files(path):
    p=FRONTEND/path
    if p.exists() and p.is_file(): return send_from_directory(FRONTEND,path)
    return send_from_directory(FRONTEND,"index.html")

@app.post("/api/auth/register")
def register():
    d=request.json or {}; name=d.get("name","").strip(); email=d.get("email","").strip().lower(); password=d.get("password","")
    if not name or not email or len(password)<6: return jsonify({"error":"Name, valid email and 6+ character password are required"}),400
    conn=db()
    try:
        cur=conn.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",(name,email,generate_password_hash(password)))
        uid=cur.lastrowid; conn.execute("INSERT INTO preferences(user_id) VALUES(?)",(uid,)); token=secrets.token_urlsafe(32); conn.execute("INSERT INTO sessions(token,user_id) VALUES(?,?)",(token,uid)); conn.commit()
    except sqlite3.IntegrityError:
        conn.close(); return jsonify({"error":"An account with this email already exists"}),409
    conn.close(); return jsonify({"token":token,"user":{"id":uid,"name":name,"email":email,"profile_completed":0}})

@app.post("/api/auth/login")
def login():
    d=request.json or {}; email=d.get("email","").strip().lower(); password=d.get("password","")
    conn=db(); row=conn.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"],password): conn.close(); return jsonify({"error":"Incorrect email or password"}),401
    token=secrets.token_urlsafe(32); conn.execute("INSERT INTO sessions(token,user_id) VALUES(?,?)",(token,row["id"])); conn.commit(); user=dict(row); conn.close(); user.pop("password_hash",None)
    return jsonify({"token":token,"user":user})

@app.post("/api/auth/logout")
def logout():
    auth=request.headers.get("Authorization","")
    if auth.startswith("Bearer "):
        conn=db(); conn.execute("DELETE FROM sessions WHERE token=?",(auth.split(" ",1)[1],)); conn.commit(); conn.close()
    return jsonify({"message":"Logged out"})

@app.get("/api/auth/me")
@auth_required
def me():
    u=dict(request.user); u.pop("password_hash",None); return jsonify(u)

@app.post("/api/setup")
@auth_required
def setup():
    d=request.json or {}; uid=request.user["id"]
    conn=db(); conn.execute("UPDATE users SET course=?,semester=?,profile_completed=1 WHERE id=?",(d.get("course","MCA"),d.get("semester","Current Semester"),uid))
    conn.execute("UPDATE preferences SET daily_hours=?,study_time=?,session_minutes=?,break_minutes=? WHERE user_id=?",(float(d.get("daily_hours",4)),d.get("study_time","Evening"),int(d.get("session_minutes",60)),int(d.get("break_minutes",15)),uid))
    conn.execute("DELETE FROM tasks WHERE user_id=?",(uid,)); conn.execute("DELETE FROM subjects WHERE user_id=?",(uid,))
    create_subjects(conn,uid,d.get("subjects",[])); conn.commit(); conn.close()
    return jsonify({"message":"Profile and study plan initialized"})

@app.get("/api/dashboard")
@auth_required
def dashboard():
    uid=request.user["id"]; conn=db(); subjects=[dict(x) for x in conn.execute("SELECT * FROM subjects WHERE user_id=? ORDER BY exam_date",(uid,))]
    total=conn.execute("SELECT COUNT(*) FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.user_id=?",(uid,)).fetchone()[0]
    completed=conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND status='Completed'",(uid,)).fetchone()[0]
    pending=conn.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND status='Pending'",(uid,)).fetchone()[0]
    avg=round(sum(s["progress"] for s in subjects)/len(subjects)) if subjects else 0; today=date.today().isoformat()
    today_tasks=[dict(x) for x in conn.execute("SELECT * FROM tasks WHERE user_id=? AND task_date=? ORDER BY start_time",(uid,today))]
    conn.close(); return jsonify({"user":{"name":request.user["name"],"course":request.user["course"]},"subjects":subjects,"stats":{"progress":avg,"completed":completed,"pending":pending,"topics":total,"streak":7},"today_tasks":today_tasks})

@app.get("/api/subjects")
@auth_required
def get_subjects():
    uid=request.user["id"]; conn=db(); rows=[dict(x) for x in conn.execute("SELECT * FROM subjects WHERE user_id=? ORDER BY exam_date",(uid,))]
    for s in rows: s["topics"]=[dict(x) for x in conn.execute("SELECT * FROM topics WHERE subject_id=?",(s["id"],))]
    conn.close(); return jsonify(rows)

@app.post("/api/subjects")
@auth_required
def add_subject():
    d=request.json; conn=db(); cur=conn.execute("INSERT INTO subjects(user_id,name,exam_date,difficulty,priority,progress) VALUES(?,?,?,?,?,?)",(request.user["id"],d["name"],d["exam_date"],d.get("difficulty","Medium"),d.get("priority","Medium"),int(d.get("progress",0)))); conn.commit(); sid=cur.lastrowid; conn.close(); return jsonify({"id":sid,"message":"Subject added"})

@app.delete("/api/subjects/<int:sid>")
@auth_required
def delete_subject(sid):
    conn=db(); conn.execute("DELETE FROM topics WHERE subject_id=?",(sid,)); conn.execute("DELETE FROM subjects WHERE id=? AND user_id=?",(sid,request.user["id"])); conn.commit(); conn.close(); return jsonify({"message":"Deleted"})

@app.post("/api/topics")
@auth_required
def add_topic():
    d=request.json; conn=db(); ok=conn.execute("SELECT id FROM subjects WHERE id=? AND user_id=?",(d["subject_id"],request.user["id"])).fetchone()
    if not ok: conn.close(); return jsonify({"error":"Invalid subject"}),403
    cur=conn.execute("INSERT INTO topics(subject_id,name,difficulty,importance,progress,estimated_minutes) VALUES(?,?,?,?,?,?)",(d["subject_id"],d["name"],d.get("difficulty","Medium"),d.get("importance","Medium"),int(d.get("progress",0)),int(d.get("estimated_minutes",60)))); conn.commit(); tid=cur.lastrowid; conn.close(); return jsonify({"id":tid,"message":"Topic added"})

@app.put("/api/topics/<int:tid>/complete")
@auth_required
def complete_topic(tid):
    conn=db(); conn.execute("UPDATE topics SET progress=100,status='Completed' WHERE id=? AND subject_id IN (SELECT id FROM subjects WHERE user_id=?)",(tid,request.user["id"])); conn.commit(); conn.close(); return jsonify({"message":"Topic completed"})

@app.get("/api/preferences")
@auth_required
def get_preferences():
    conn=db(); row=conn.execute("SELECT * FROM preferences WHERE user_id=?",(request.user["id"],)).fetchone(); conn.close(); return jsonify(dict(row) if row else {})

@app.put("/api/preferences")
@auth_required
def update_preferences():
    d=request.json; conn=db(); conn.execute("UPDATE preferences SET daily_hours=?,study_time=?,session_minutes=?,break_minutes=? WHERE user_id=?",(float(d["daily_hours"]),d["study_time"],int(d["session_minutes"]),int(d["break_minutes"]),request.user["id"])); conn.commit(); conn.close(); return jsonify({"message":"Preferences saved"})

@app.post("/api/study-plan/generate")
@auth_required
def generate_plan():
    uid=request.user["id"]; conn=db(); pref=dict(conn.execute("SELECT * FROM preferences WHERE user_id=?",(uid,)).fetchone()); subjects=[dict(x) for x in conn.execute("SELECT * FROM subjects WHERE user_id=?",(uid,))]; tasks=[]
    for s in subjects:
        for t in conn.execute("SELECT * FROM topics WHERE subject_id=? AND progress<100",(s["id"],)):
            td=dict(t); tasks.append((priority_score(td,s),s,td))
    tasks.sort(key=lambda x:x[0],reverse=True); conn.execute("DELETE FROM tasks WHERE user_id=? AND task_date>=?",(uid,date.today().isoformat()))
    minutes=max(60,int(float(pref["daily_hours"])*60)); session=int(pref["session_minutes"]); breakm=int(pref["break_minutes"]); slots=max(1,minutes//(session+breakm)); start={"Morning":8,"Afternoon":13,"Evening":18,"Night":21}.get(pref["study_time"],18); created=[]
    for off in range(7):
        if not tasks: break
        d=date.today()+timedelta(days=off); used=0
        for _ in range(slots):
            if not tasks: break
            score,s,t=tasks.pop(0); dur=min(session,int(t["estimated_minutes"])); hour=start+used//60; minute=used%60; st=f"{hour:02d}:{minute:02d}"
            cur=conn.execute("INSERT INTO tasks(user_id,topic_id,subject,topic,task_date,start_time,duration,status,priority_score) VALUES(?,?,?,?,?,?,?,?,?)",(uid,t["id"],s["name"],t["name"],d.isoformat(),st,dur,"Pending",score)); created.append({"id":cur.lastrowid,"subject":s["name"],"topic":t["name"],"task_date":d.isoformat(),"start_time":st,"duration":dur,"status":"Pending","priority_score":score}); used+=dur+breakm
            if used>=minutes: break
    conn.commit(); conn.close(); return jsonify({"message":"Personalized plan generated","tasks":created,"count":len(created)})

@app.get("/api/tasks")
@auth_required
def get_tasks():
    conn=db(); rows=[dict(x) for x in conn.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY task_date,start_time",(request.user["id"],))]; conn.close(); return jsonify(rows)

@app.put("/api/tasks/<int:tid>/complete")
@auth_required
def complete_task(tid):
    conn=db(); conn.execute("UPDATE tasks SET status='Completed' WHERE id=? AND user_id=?",(tid,request.user["id"])); conn.commit(); conn.close(); return jsonify({"message":"Task completed"})

@app.put("/api/tasks/<int:tid>/skip")
@auth_required
def skip_task(tid):
    conn=db(); conn.execute("UPDATE tasks SET status='Skipped' WHERE id=? AND user_id=?",(tid,request.user["id"])); conn.commit(); conn.close(); return jsonify({"message":"Task skipped"})

@app.get("/api/analytics")
@auth_required
def analytics():
    uid=request.user["id"]; conn=db(); subject=[dict(x) for x in conn.execute("SELECT name,progress FROM subjects WHERE user_id=?",(uid,))]; statuses=[dict(x) for x in conn.execute("SELECT status,COUNT(*) count FROM tasks WHERE user_id=? GROUP BY status",(uid,))]; hours=conn.execute("SELECT COALESCE(SUM(duration),0) FROM tasks WHERE user_id=? AND status='Completed'",(uid,)).fetchone()[0]/60; conn.close(); return jsonify({"subjects":subject,"statuses":statuses,"completed_hours":round(hours,1)})

init_db()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
