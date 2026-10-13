from flask import Flask, render_template, request, jsonify
import random
import math
from datetime import datetime, timedelta
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Users table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','tester','developer')),
            name TEXT,
            address TEXT,
            city TEXT,
            mobile TEXT,
            age INTEGER,
            experience TEXT,
            department TEXT,
            join_date TEXT,
            active INTEGER DEFAULT 1
        )
        """
    )

    # Bugs table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            component TEXT NOT NULL,
            assignee TEXT,
            reporter TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    # System health metrics table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS system_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TEXT NOT NULL,
            cpu_percent INTEGER,
            memory_percent INTEGER,
            uptime_hours INTEGER,
            error_rate REAL,
            status TEXT
        )
        """
    )

    # AI training data table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_training (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checked_at TEXT NOT NULL,
            total_samples INTEGER,
            processed_today INTEGER,
            accuracy_improvement REAL
        )
        """
    )

    # Code files table for backend-only operations (exactly 10 seeded files)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS code_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            language TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # Test cases table (migration-safe)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            component TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            last_run TEXT,
            owner TEXT
        )
        """
    )
    # Test plans table (migration-safe)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS test_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            version TEXT NOT NULL,
            owner TEXT NOT NULL,
            total_cases INTEGER NOT NULL,
            last_updated TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    # Seed users if empty
    cur.execute("SELECT COUNT(*) as c FROM users")
    if cur.fetchone()[0] == 0:
        first_names = ['Arjun', 'Priya', 'Rajesh', 'Sneha', 'Vikram', 'Anita', 'Suresh', 'Kavita', 'Rahul', 'Deepa', 'Amit', 'Sunita']
        last_names = ['Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Verma', 'Jain', 'Malhotra', 'Reddy', 'Nair', 'Iyer']
        rand_name = lambda: f"{random.choice(first_names)} {random.choice(last_names)}"
        seed_users = [
            ('admin@ebug.com', 'admin123', 'admin', 'Admin', '221 MG Road', 'Mumbai', '+91-90000-12345', 30, '10 years', 'Engineering', '2023-01-10', 1),
            ('tester@ebug.com', 'tester123', 'tester', rand_name(), '11 Park Street', 'Kolkata', '+91-90000-22222', 27, '5 years', 'QA', '2023-03-12', 1),
            ('developer@ebug.com', 'dev123', 'developer', rand_name(), '7 Brigade Road', 'Bangalore', '+91-90000-33333', 29, '7 years', 'Engineering', '2022-11-05', 1)
        ]
        cur.executemany(
            """
            INSERT INTO users (email, password, role, name, address, city, mobile, age, experience, department, join_date, active)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            seed_users,
        )

    # Seed some bugs if empty
    cur.execute("SELECT COUNT(*) as c FROM bugs")
    if cur.fetchone()[0] == 0:
        severities = ['critical', 'high', 'medium', 'low']
        statuses = ['open', 'in progress', 'resolved', 'closed']
        components = ['frontend', 'backend', 'database', 'api', 'mobile']
        titles = [
            'App crash on launch', 'Login fails intermittently', 'Slow dashboard loading',
            'API returns 500 error', 'UI overlap on small screens', 'Memory leak in worker',
            'Notification duplicates', 'Search results inaccurate'
        ]
        seed_bugs = []
        for i in range(1, 10):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 200))
            seed_bugs.append(
                (
                    random.choice(titles),
                    random.choice(severities),
                    random.choice(statuses),
                    random.choice(components),
                    random.choice(['Dev A', 'Dev B', 'Dev C', 'QA Team']),
                    random.choice(['Tester X', 'Tester Y', 'User Z']),
                    created_at.isoformat() + 'Z',
                )
            )
        cur.executemany(
            """
            INSERT INTO bugs (title, severity, status, component, assignee, reporter, created_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            seed_bugs,
        )

    # Seed 10 sample code files if empty
    cur.execute("SELECT COUNT(*) FROM code_files")
    if cur.fetchone()[0] == 0:
        now = datetime.utcnow().isoformat() + 'Z'
        samples = [
            ("auth_middleware.py", "python", "\n".join([
                "from functools import wraps",
                "from flask import request, jsonify",
                "",
                "def require_role(roles):",
                "    def decorator(fn):",
                "        @wraps(fn)",
                "        def wrapper(*args, **kwargs):",
                "            role = request.headers.get('X-Role', '')",
                "            if role not in roles:",
                "                return jsonify({'error': 'forbidden'}), 403",
                "            return fn(*args, **kwargs)",
                "        return wrapper",
                "    return decorator",
                "",
                "@require_role(['admin'])",
                "def admin_only():",
                "    return jsonify({'ok': True})",
                "",
                "def get_user_id():",
                "    return request.headers.get('X-User-Id', '0')",
            ]) ),
            ("bug_utils.js", "javascript", "\n".join([
                "export function groupBySeverity(bugs){",
                "  const out = {critical:0, high:0, medium:0, low:0};",
                "  bugs.forEach(b=>out[b.severity]=(out[b.severity]||0)+1);",
                "  return out;",
                "}",
                "",
                "export function recent(bugs, hours){",
                "  const t = Date.now() - hours*3600*1000;",
                "  return bugs.filter(b=> new Date(b.createdAt).getTime() >= t);",
                "}",
                "",
                "export function toCsv(bugs){",
                "  const header = 'id,title,severity,status\\n';",
                "  const rows = bugs.map(b=>`${b.id},${b.title},${b.severity},${b.status}`).join('\\n');",
                "  return header + rows;",
                "}",
                "",
                "export const COLORS = ['#ff6384','#ff9f40','#4bc0c0','#36a2eb'];",
            ]) ),
            ("db_migrations.sql", "sql", "\n".join([
                "-- Create new table for tags",
                "CREATE TABLE IF NOT EXISTS tags (",
                "  id INTEGER PRIMARY KEY AUTOINCREMENT,",
                "  name TEXT UNIQUE NOT NULL",
                ");",
                "-- Add tag_id to bugs",
                "ALTER TABLE bugs ADD COLUMN tag_id INTEGER;",
                "-- Create index",
                "CREATE INDEX IF NOT EXISTS idx_bugs_tag ON bugs(tag_id);",
                "-- Seed tags",
                "INSERT OR IGNORE INTO tags(name) VALUES ('performance'),('ui'),('backend'),('api');",
                "-- Done",
            ]) ),
            ("analytics_calc.py", "python", "\n".join([
                "from collections import Counter",
                "",
                "def calc_trends(reports):",
                "    days = Counter(r['createdAt'][:10] for r in reports)",
                "    return sorted(days.items())",
                "",
                "def assignment_breakdown(reports):",
                "    c = Counter(r.get('assignee','Unassigned') for r in reports)",
                "    return dict(c)",
                "",
                "def normalize(series):",
                "    if not series: return []",
                "    m = max(series)",
                "    return [ round((x/m) if m else 0, 2) for x in series ]",
                "",
                "def top_n(mapping, n=5):",
                "    return sorted(mapping.items(), key=lambda x:x[1], reverse=True)[:n]",
            ]) ),
            ("config.yaml", "yaml", "\n".join([
                "app:",
                "  name: ebug-tracker",
                "  debug: true",
                "server:",
                "  host: 127.0.0.1",
                "  port: 5000",
                "database:",
                "  driver: sqlite",
                "  path: app.db",
                "auth:",
                "  roles: [admin, tester, developer]",
                "features:",
                "  analytics: true",
                "  ai: true",
            ]) ),
            ("queue_worker.py", "python", "\n".join([
                "import time",
                "def work(jobs):",
                "    processed = 0",
                "    for job in jobs:",
                "        time.sleep(0.01)",
                "        processed += 1",
                "    return processed",
                "",
                "class Worker:",
                "    def __init__(self, name):",
                "        self.name = name",
                "    def run(self, jobs):",
                "        return work(jobs)",
                "",
                "if __name__ == '__main__':",
                "    print(Worker('w').run([1]*20))",
            ]) ),
            ("report_validator.js", "javascript", "\n".join([
                "export function validateTitle(t){ return !!t && t.length>3; }",
                "export function validateSeverity(s){",
                "  return ['critical','high','medium','low'].includes(s);",
                "}",
                "export function validateReport(r){",
                "  return validateTitle(r.title) && validateSeverity(r.severity);",
                "}",
                "export function sanitize(t){",
                "  return String(t||'').replace(/\n/g,' ').slice(0,120);",
                "}",
                "export function pad(n){ return (n<10?'0':'')+n; }",
            ]) ),
            ("http_client.py", "python", "\n".join([
                "import json, urllib.request",
                "def get(url):",
                "    with urllib.request.urlopen(url) as r:",
                "        return json.loads(r.read().decode())",
                "def post(url, data):",
                "    req = urllib.request.Request(url, method='POST',",
                "        data=json.dumps(data).encode(),",
                "        headers={'Content-Type':'application/json'})",
                "    with urllib.request.urlopen(req) as r:",
                "        return json.loads(r.read().decode())",
                "def head(url):",
                "    req = urllib.request.Request(url, method='HEAD')",
                "    with urllib.request.urlopen(req) as r:",
                "        return dict(r.headers)",
            ]) ),
            ("readme.md", "markdown", "\n".join([
                "# E-Bug Sample Library",
                "",
                "This folder stores sample code artifacts used for demonstrations.",
                "- 10 files are pre-seeded in the database.",
                "- Only update operations are allowed via the API.",
                "- Creation and deletion are blocked.",
                "",
                "Use the API to fetch and update content.",
                "",
                "```bash",
                "curl /api/code_files",
                "```",
            ]) ),
            ("style.css", "css", "\n".join([
                "/* sample stylesheet */",
                "body{font-family:system-ui, sans-serif;}",
                ".card{border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.1);}",
                ".btn{padding:8px 12px;border-radius:6px;}",
                ".btn-primary{background:#1f78c1;color:#fff;}",
                ".muted{color:#888;}",
                "header,footer{padding:12px;}",
                ".grid{display:grid;gap:12px;grid-template-columns:1fr 1fr;}",
                ".code{font-family:monospace;background:#f7f7f7;padding:8px;border-radius:6px;}",
                ".pill{border-radius:999px;padding:2px 8px;background:#eee;}",
                ".ok{color:#2ecc71}",
            ]) ),
            ("utils.go", "go", "\n".join([
                "package utils",
                "import \"strings\"",
                "func Slug(s string) string {",
                "  s = strings.ToLower(strings.TrimSpace(s))",
                "  s = strings.ReplaceAll(s, \" \", \"-\")",
                "  return s",
                "}",
                "func Clamp(n, min, max int) int {",
                "  if n < min { return min }",
                "  if n > max { return max }",
                "  return n",
                "}",
                "func Repeat(s string, n int) string {",
                "  out := \"\"",
                "  for i:=0;i<n;i++{ out += s }",
                "  return out",
                "}",
            ]) ),
        ]
        cur.executemany(
            "INSERT INTO code_files (name, language, content, created_at, updated_at) VALUES (?,?,?,?,?)",
            [(n, l, c, now, now) for (n,l,c) in samples]
        )

    # Seed test cases if empty
    cur.execute("SELECT COUNT(*) FROM test_cases")
    if cur.fetchone()[0] == 0:
        now = datetime.utcnow().isoformat() + 'Z'
        cases = [
            ("TC-101", "Login with valid credentials", "auth", "High", "Passed", now, "QA Tester"),
            ("TC-102", "Login with invalid password", "auth", "Medium", "Passed", now, "QA Tester"),
            ("TC-103", "Create new bug report", "frontend", "High", "Failed", now, "QA Tester"),
            ("TC-104", "Search bug by title", "api", "Low", "Blocked", now, "QA Tester"),
            ("TC-105", "Update bug status", "backend", "High", "Passed", now, "QA Tester"),
            ("TC-106", "Assign bug to developer", "backend", "Medium", "Passed", now, "QA Tester"),
            ("TC-107", "System health fetch", "api", "Low", "Passed", now, "QA Tester"),
            ("TC-108", "AI config snapshot", "ai", "Medium", "Passed", now, "QA Tester"),
        ]
        cur.executemany(
            "INSERT INTO test_cases (key, title, component, priority, status, last_run, owner) VALUES (?,?,?,?,?,?,?)",
            cases,
        )
    # Seed test plans if empty
    cur.execute("SELECT COUNT(*) FROM test_plans")
    if cur.fetchone()[0] == 0:
        now = datetime.utcnow().isoformat() + 'Z'
        plans = [
            ("Regression Suite", "v1.2", "QA Lead", 120, now, "Active"),
            ("Smoke Tests", "v1.2", "QA Lead", 25, now, "Active"),
            ("Performance Benchmarks", "v1.0", "QA Lead", 15, now, "Draft"),
        ]
        cur.executemany(
            "INSERT INTO test_plans (name, version, owner, total_cases, last_updated, status) VALUES (?,?,?,?,?,?)",
            plans,
        )

    conn.commit()
    conn.close()


init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if row and row['password'] == password and (role is None or row['role'] == role):
        return jsonify({
            "success": True,
            "message": "Login successful!",
            "user": {
                "id": row['id'],
                "email": row['email'],
                "role": row['role'],
                "name": row['name'] or row['email'],
            }
        })
    return jsonify({"success": False, "message": "Invalid credentials!"}), 401

# --- Interactive API endpoints ---

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM users").fetchall()
    conn.close()
    users = []
    for r in rows:
        users.append({
            'id': r['id'],
            'name': r['name'] or r['email'],
            'email': r['email'],
            'role': r['role'],
            'active': bool(r['active']),
            'full_name': r['name'] or r['email'],
            'address': r['address'],
            'city': r['city'],
            'mobile': r['mobile'],
            'age': r['age'],
            'experience': r['experience'],
            'department': r['department'],
            'join_date': r['join_date']
        })
    summary = {
        'total': len(users),
        'admins': sum(1 for u in users if u['role'] == 'admin'),
        'testers': sum(1 for u in users if u['role'] == 'tester'),
        'developers': sum(1 for u in users if u['role'] == 'developer')
    }
    return jsonify({'summary': summary, 'users': users})


@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    fields = (
        data.get('email'), data.get('password'), data.get('role'), data.get('name'),
        data.get('address'), data.get('city'), data.get('mobile'), data.get('age'),
        data.get('experience'), data.get('department'), data.get('join_date'), 1 if data.get('active', True) else 0
    )
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO users (email, password, role, name, address, city, mobile, age, experience, department, join_date, active)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            fields,
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({'id': new_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 409


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    data = request.get_json()
    allowed = ['email', 'password', 'role', 'name', 'address', 'city', 'mobile', 'age', 'experience', 'department', 'join_date', 'active']
    sets = []
    values = []
    for k in allowed:
        if k in data:
            sets.append(f"{k} = ?")
            values.append(data[k])
    if not sets:
        return jsonify({'error': 'No fields to update'}), 400
    values.append(user_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return jsonify({'error': 'User not found'}), 404
    role = r['role']
    user_details = {
        'id': r['id'],
        'name': r['name'] or r['email'],
        'email': r['email'],
        'role': role,
        'active': bool(r['active']),
        'full_name': r['name'] or r['email'],
        'address': r['address'],
        'city': r['city'],
        'mobile': r['mobile'],
        'age': r['age'],
        'experience': r['experience'],
        'department': r['department'],
        'join_date': r['join_date'],
        'skills': random.sample(['Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL', 'Docker', 'AWS', 'Git'], random.randint(3, 6)),
        'projects': random.randint(5, 25),
        'bugs_resolved': random.randint(10, 100) if role == 'developer' else random.randint(5, 50),
        'last_login': datetime.utcnow().isoformat() + 'Z'
    }
    return jsonify(user_details)


@app.route('/api/system_health', methods=['GET'])
def system_health():
    cpu = random.randint(5, 65)
    memory = random.randint(10, 70)
    uptime_hours = random.randint(12, 480)
    error_rate = round(random.uniform(0.0, 1.5), 2)
    status = 'Healthy' if cpu < 70 and memory < 75 and error_rate < 2.0 else 'Degraded'
    checked_at = datetime.utcnow().isoformat() + 'Z'

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO system_health (checked_at, cpu_percent, memory_percent, uptime_hours, error_rate, status) VALUES (?,?,?,?,?,?)",
        (checked_at, cpu, memory, uptime_hours, error_rate, status),
    )
    conn.commit()
    conn.close()

    components = [
        {'name': 'API Gateway', 'status': random.choice(['OK', 'OK', 'OK', 'WARN'])},
        {'name': 'Auth Service', 'status': random.choice(['OK', 'OK', 'WARN'])},
        {'name': 'Database', 'status': random.choice(['OK', 'OK', 'OK', 'OK', 'WARN'])},
        {'name': 'Worker Queue', 'status': random.choice(['OK', 'OK', 'WARN'])}
    ]
    return jsonify({
        'status': status,
        'metrics': {
            'cpuPercent': cpu,
            'memoryPercent': memory,
            'uptimeHours': uptime_hours,
            'errorRatePct': error_rate
        },
        'components': components,
        'checkedAt': checked_at
    })


@app.route('/api/bug_reports', methods=['GET'])
def bug_reports():
    # Randomly add or close bugs to simulate dynamic changes
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bugs")
    total = cur.fetchone()[0]
    action = random.choice(['add', 'close', 'none'])
    if action == 'add' or total == 0:
        severities = ['critical', 'high', 'medium', 'low']
        statuses = ['open', 'in progress', 'resolved', 'closed']
        components = ['frontend', 'backend', 'database', 'api', 'mobile']
        titles = [
            'Intermittent API timeout', 'Form validation fails', 'High CPU spike during peak',
            'Crash on logout', 'Session not persisting', 'UI glitch on resize'
        ]
        created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        cur.execute(
            """
            INSERT INTO bugs (title, severity, status, component, assignee, reporter, created_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                random.choice(titles),
                random.choice(severities),
                random.choice(statuses),
                random.choice(components),
                random.choice(['Dev A', 'Dev B', 'Dev C', 'QA Team']),
                random.choice(['Tester X', 'Tester Y', 'User Z']),
                created_at.isoformat() + 'Z',
            ),
        )
    elif action == 'close':
        cur.execute("UPDATE bugs SET status='closed' WHERE status!='closed' AND id IN (SELECT id FROM bugs ORDER BY RANDOM() LIMIT 1)")
    conn.commit()

    rows = cur.execute("SELECT * FROM bugs ORDER BY datetime(created_at) DESC LIMIT 100").fetchall()
    conn.close()

    reports = []
    for r in rows:
        reports.append({
            'id': r['id'],
            'title': r['title'],
            'severity': r['severity'],
            'status': r['status'],
            'component': r['component'],
            'assignee': r['assignee'],
            'reporter': r['reporter'],
            'createdAt': r['created_at']
        })

    severities = ['critical', 'high', 'medium', 'low']
    summary = {
        'total': len(reports),
        'bySeverity': {s: sum(1 for r in reports if r['severity'] == s) for s in severities},
        'open': sum(1 for r in reports if r['status'] in ['open', 'in progress'])
    }
    return jsonify({'summary': summary, 'reports': reports})


@app.route('/api/ai_config', methods=['GET'])
def ai_config():
    # Persist training snapshot to DB for history and return latest snapshot
    training_data = {
        'total_samples': random.randint(5000, 15000),
        'processed_today': random.randint(50, 200),
        'accuracy_improvement': round(random.uniform(0.5, 3.2), 1)
    }
    checked_at = datetime.utcnow().isoformat() + 'Z'

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ai_training (checked_at, total_samples, processed_today, accuracy_improvement) VALUES (?,?,?,?)",
        (checked_at, training_data['total_samples'], training_data['processed_today'], training_data['accuracy_improvement'])
    )
    conn.commit()
    conn.close()

    models = [
        {'name': 'Severity Predictor', 'status': 'Active', 'accuracy': 87, 'last_trained': checked_at[:10]},
        {'name': 'Duplicate Detector', 'status': 'Active', 'accuracy': 95, 'last_trained': checked_at[:10]},
        {'name': 'Auto Assignment', 'status': 'Training', 'accuracy': 78, 'last_trained': checked_at[:10]},
        {'name': 'Trend Analyzer', 'status': 'Active', 'accuracy': 82, 'last_trained': checked_at[:10]}
    ]
    return jsonify({
        'models': models,
        'training_data': training_data,
        'system_status': 'Operational',
        'next_training': checked_at
    })


@app.route('/api/analytics', methods=['GET'])
def analytics():
    # Compute analytics from DB bugs
    conn = get_db_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT severity, status, assignee, created_at FROM bugs").fetchall()
    conn.close()

    # Status counts
    status_labels = ['Open', 'In Progress', 'Resolved', 'Closed']
    status_map = {'open': 'Open', 'in progress': 'In Progress', 'resolved': 'Resolved', 'closed': 'Closed'}
    status_counts = {k: 0 for k in status_labels}
    for r in rows:
        status_counts[status_map.get(r['status'], 'Open')] += 1
    status_data = {
        'labels': status_labels,
        'data': [status_counts[l] for l in status_labels],
        'colors': ['#ff6384', '#ff9f40', '#4bc0c0', '#36a2eb']
    }

    # Severity distribution
    sev_labels = ['Critical', 'High', 'Medium', 'Low']
    sev_map = {'critical': 'Critical', 'high': 'High', 'medium': 'Medium', 'low': 'Low'}
    sev_counts = {k: 0 for k in sev_labels}
    for r in rows:
        sev_counts[sev_map.get(r['severity'], 'Low')] += 1
    severity_data = {
        'labels': sev_labels,
        'data': [sev_counts[l] for l in sev_labels],
        'colors': ['#ff6384', '#ff9f40', '#ffcd56', '#4bc0c0']
    }

    # Bug trends over last 7 days
    today = datetime.utcnow().date()
    trend_labels = []
    trend_values = []
    for i in range(7):
        d = today - timedelta(days=6 - i)
        trend_labels.append(d.strftime('%m/%d'))
        count = 0
        for r in rows:
            try:
                rd = datetime.fromisoformat(r['created_at'].replace('Z', '')).date()
                if rd == d:
                    count += 1
            except Exception:
                pass
        trend_values.append(count)
    trends_data = {
        'labels': trend_labels,
        'data': trend_values,
        'color': '#36a2eb'
    }

    # Assignment distribution (top assignees)
    labels = []
    counts = {}
    for r in rows:
        a = r['assignee'] or 'Unassigned'
        counts[a] = counts.get(a, 0) + 1
    # Take top 5 + Unassigned
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    labels = [k for k, _ in sorted_items]
    values = [v for _, v in sorted_items]
    if 'Unassigned' not in labels:
        labels.append('Unassigned')
        values.append(counts.get('Unassigned', 0))
    assignment_data = {
        'labels': labels,
        'data': values,
        'colors': ['#ff6384', '#ff9f40', '#ffcd56', '#4bc0c0', '#36a2eb', '#9966ff']
    }

    return jsonify({
        'status_overview': status_data,
        'severity_distribution': severity_data,
        'bug_trends': trends_data,
        'assignment_distribution': assignment_data
    })


def _parse_iso8601(value: str):
    if not value:
        return None
    cleaned = value
    if cleaned.endswith('Z'):
        cleaned = cleaned.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


@app.route('/api/tests_today', methods=['GET'])
def tests_today():
    conn = get_db_connection()
    cur = conn.cursor()
    db_rows = cur.execute(
        "SELECT key, title, component, priority, status, last_run, owner FROM test_cases ORDER BY key"
    ).fetchall()
    rows = [dict(r) for r in db_rows]

    today = datetime.utcnow().date()
    updates = []

    if rows:
        for row in rows:
            parsed = _parse_iso8601(row['last_run']) if row['last_run'] else None
            row['_parsed_last_run'] = parsed

        completed_today = [row for row in rows if row['_parsed_last_run'] and row['_parsed_last_run'].date() == today]
        target_completed = max(1, math.ceil(len(rows) * 0.4))
        needed = max(0, target_completed - len(completed_today))

        if needed:
            eligible = [
                row for row in rows
                if (not row['_parsed_last_run'] or row['_parsed_last_run'].date() != today)
                and (row['status'] or '').lower() != 'blocked'
            ]
            random.shuffle(eligible)
            for row in eligible[:needed]:
                new_ts = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
                row['last_run'] = new_ts
                parsed = _parse_iso8601(new_ts)
                row['_parsed_last_run'] = parsed
                updates.append((new_ts, row['key']))

        if updates:
            cur.executemany("UPDATE test_cases SET last_run = ? WHERE key = ?", updates)
            conn.commit()
    else:
        rows = []

    completed = []
    pending = []

    for r in rows:
        last_run = r['last_run']
        parsed_last_run = r.get('_parsed_last_run') or (_parse_iso8601(last_run) if last_run else None)
        ran_today = parsed_last_run.date() == today if parsed_last_run else False
        payload = {
            'key': r['key'],
            'title': r['title'],
            'component': r['component'],
            'priority': r['priority'],
            'status': r['status'],
            'lastRun': last_run,
            'owner': r['owner']
        }
        (completed if ran_today else pending).append(payload)

    total = len(rows)
    completed_count = len(completed)
    pending_count = len(pending)
    completion_pct = round((completed_count / total) * 100, 1) if total else 0

    conn.close()
    return jsonify({
        'date': today.isoformat(),
        'totalTests': total,
        'completedToday': completed_count,
        'pendingToday': pending_count,
        'completionPct': completion_pct,
        'completed': completed,
        'pending': pending
    })

# ---------------- Code Files API (restricted to seeded 10) -----------------

def _is_valid_code_file_id(file_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM code_files WHERE id = ?", (file_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row)


@app.route('/api/code_files', methods=['GET'])
def list_code_files():
    conn = get_db_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT id, name, language, updated_at FROM code_files ORDER BY name").fetchall()
    conn.close()
    return jsonify([
        {'id': r['id'], 'name': r['name'], 'language': r['language'], 'updatedAt': r['updated_at']} for r in rows
    ])


@app.route('/api/code_files/<int:file_id>', methods=['GET'])
def get_code_file(file_id: int):
    if not _is_valid_code_file_id(file_id):
        return jsonify({'error': 'File not found'}), 404
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM code_files WHERE id = ?", (file_id,))
    r = cur.fetchone()
    conn.close()
    return jsonify({
        'id': r['id'],
        'name': r['name'],
        'language': r['language'],
        'content': r['content'],
        'createdAt': r['created_at'],
        'updatedAt': r['updated_at']
    })


@app.route('/api/code_files/<int:file_id>', methods=['PUT'])
def update_code_file(file_id: int):
    if not _is_valid_code_file_id(file_id):
        return jsonify({'error': 'File not found'}), 404
    data = request.get_json() or {}
    allowed_fields = {'name', 'content', 'language'}
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    if not updates:
        return jsonify({'error': 'No updatable fields provided'}), 400
    updates['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [file_id]
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"UPDATE code_files SET {set_clause} WHERE id = ?", values)
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Duplicate name not allowed'}), 409
    conn.close()
    return jsonify({'success': True})


@app.route('/api/code_files', methods=['POST'])
def create_code_file():
    data = request.get_json() or {}
    name = data.get('name')
    language = data.get('language')
    content = data.get('content')
    if not name or not language or not content:
        return jsonify({'error': 'name, language, and content are required'}), 400
    now = datetime.utcnow().isoformat() + 'Z'
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO code_files (name, language, content, created_at, updated_at) VALUES (?,?,?,?,?)",
            (name, language, content, now, now),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({'id': new_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Duplicate name not allowed'}), 409


@app.route('/api/code_files/<int:file_id>', methods=['DELETE'])
def delete_code_file(file_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM code_files WHERE id = ?", (file_id,))
    if cur.rowcount == 0:
        conn.close()
        return jsonify({'error': 'File not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
