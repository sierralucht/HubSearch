from flask import Flask, render_template, redirect, url_for, request
from github import Github
import sqlite3
import base64

app = Flask(__name__)
app.secret_key = "changenonononono"

PAYLOAD = "header(\"Location: $_GET language:php"
BLACKLIST = ["test", "example", "mock", "attack", "injection", "vuln"]


def create_database():
    conn = sqlite3.connect('search.db')

    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS search(watchers INTEGER, code text, url text PRIMARY KEY, positive INTEGER)''')
    conn.commit()
    c.close()

    return conn


def insert_code(code, conn):
    c = conn.cursor()
    try:
        c.execute('''INSERT OR IGNORE INTO search(watchers, code, url, positive) VALUES (?,?,?,0)''',
                  (code.repository.stargazers_count + code.repository.watchers, unicode(base64.b64decode(code.content), 'utf-8'),
                   code.html_url))
    except sqlite3.ProgrammingError as e:
        print 'Error: %s' % str(e)
        print '%d, %s %s' % (code.repository.stargazers_count + code.repository.watchers,
                             unicode(base64.b64decode(code.content), 'utf-8'),code.html_url)
        c.close()
    conn.commit()
    c.close()


def get_code(conn, limit=1000):
    c = conn.cursor()
    c.execute('''SELECT * from search ORDER BY watchers DESC LIMIT ?''', (limit,))
    results = c.fetchall()
    c.close()

    return results


def read_credentials():
    with open("../p.txt", "r") as f:
        lines = f.readlines()
        user = lines[0].strip()
        pw = lines[1].strip()

    return user, pw


def search_code(g, limit=500):
    l = g.search_code(PAYLOAD)

    most_popular = {}
    try:
        for code in set(l[:limit]):
            if any(s in code.html_url.lower() for s in BLACKLIST):
                continue
            if code.repository.stargazers_count + code.repository.watchers not in most_popular:
                most_popular[code.repository.stargazers_count + code.repository.watchers] = [code]
            else:
                most_popular[code.repository.stargazers_count + code.repository.watchers].append(code)
    except Exception as e:
        print str(e)
        print g.get_rate_limit()
        print len(most_popular)
        return most_popular

    print len(most_popular)
    return most_popular


@app.route('/', methods=['GET', 'POST'])
def index():
    user, pw = read_credentials()
    code = []
    try:
        g = Github(user, pw)
        conn = create_database()
        most_popular = search_code(g, limit=500)
        for key in most_popular:
            for instance in most_popular[key]:
                insert_code(instance, conn)

        code = get_code(conn)
    except Exception as e:
        message = str(e)

    return render_template('index.html', message=message, code=code)

if __name__ == "__main__":
    app.run()
