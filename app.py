from flask import Flask, request, render_template, redirect
import requests
import sqlite3
import os

app = Flask(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY,
        ip TEXT,
        country TEXT,
        city TEXT,
        isp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return "IP Tracker is running 🚀"

# ---------------- TRACK PAGE (CONSENT) ----------------
@app.route('/track/<code>')
def track(code):
    return render_template("track.html", code=code)

# ---------------- LOG + REDIRECT ----------------
@app.route('/go/<code>')
def go(code):

    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    try:
        res = requests.get(f"http://ip-api.com/json/{user_ip}").json()
    except:
        res = {"country":"Unknown","city":"Unknown","isp":"Unknown"}

    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO logs (ip, country, city, isp)
        VALUES (?,?,?,?)
    """, (user_ip, res.get('country'), res.get('city'), res.get('isp')))

    conn.commit()
    conn.close()

    # redirect destination (demo)
    return redirect("https://google.com")

# ---------------- LOG VIEW ----------------
@app.route('/logs')
def logs():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM logs ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()

    return str(data)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)