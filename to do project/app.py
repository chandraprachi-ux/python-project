from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        task TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        session["email"] = email
        return redirect("/home")

    return render_template("login.html")

# ---------- HOME ----------
@app.route("/home")
def home():
    if "email" not in session:
        return redirect("/")

    email = session["email"]

    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE email=?", (email,))
    tasks = cursor.fetchall()

    now = datetime.now()
    updated_tasks = []

    for t in tasks:
        task_id, email, task, deadline, status = t

        # FIX: safe deadline check
        if status == "pending" and deadline:
            try:
                if now > datetime.fromisoformat(deadline):
                    cursor.execute(
                        "UPDATE tasks SET status='expired' WHERE id=?",
                        (task_id,)
                    )
                    conn.commit()
                    status = "expired"
            except:
                pass

        updated_tasks.append((task_id, email, task, deadline, status))

    conn.close()

    return render_template("home.html", tasks=updated_tasks, email=email)

# ---------- ADD TASK ----------
@app.route("/add", methods=["POST"])
def add():
    if "email" not in session:
        return redirect("/")

    email = session["email"]
    task = request.form["task"]
    deadline = request.form["deadline"]

    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (email, task, deadline, status)
        VALUES (?, ?, ?, 'pending')
    """, (email, task, deadline))

    conn.commit()
    conn.close()

    return redirect("/home")

# ---------- COMPLETE ----------
@app.route("/complete/<int:id>")
def complete(id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE tasks SET status='completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/home")

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/home")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)