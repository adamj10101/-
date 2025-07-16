from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'todo.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    filter_status = request.args.get('filter', 'all')
    conn = get_db_connection()
    if filter_status == 'active':
        tasks = conn.execute('SELECT * FROM tasks WHERE done = 0 ORDER BY created_at DESC').fetchall()
    elif filter_status == 'done':
        tasks = conn.execute('SELECT * FROM tasks WHERE done = 1 ORDER BY created_at DESC').fetchall()
    else:
        tasks = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks, filter_status=filter_status)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title'].strip()
    if title:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO tasks (title, done, created_at) VALUES (?, ?, ?)',
            (title, False, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT done FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task:
        new_status = 0 if task['done'] else 1
        conn.execute('UPDATE tasks SET done = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit(task_id):
    new_title = request.form.get('new_title', '').strip()
    if new_title:
        conn = get_db_connection()
        conn.execute('UPDATE tasks SET title = ? WHERE id = ?', (new_title, task_id))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
