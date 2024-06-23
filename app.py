from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
from flask_frozen import Freezer

app = Flask(__name__)
freezer = Freezer(app)

def init_db():
    with sqlite3.connect("posts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY date DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()
    conn.close()
    return render_template('post.html', post=post)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect("posts.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO posts (title, content, date) VALUES (?, ?, ?)", (title, content, date))
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit_post.html', post=None)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cursor.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute("UPDATE posts SET title=?, content=? WHERE id=?", (title, content, post_id))
        conn.commit()
        conn.close()
        return redirect(url_for('post', post_id=post_id))
    conn.close()
    return render_template('edit_post.html', post=post)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form['query']
    search_by = request.form['search_by']
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    if search_by == 'title':
        cursor.execute("SELECT * FROM posts WHERE title LIKE ?", ('%' + query + '%',))
    else:
        cursor.execute("SELECT * FROM posts WHERE date LIKE ?", ('%' + query + '%',))
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@freezer.register_generator
def post_generator():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM posts")
    posts = cursor.fetchall()
    conn.close()
    for post in posts:
        yield 'post', {'post_id': post[0]}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
