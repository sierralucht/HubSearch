from flask import Flask, render_template, redirect, url_for, request
from github import Github

app = Flask(__name__)
app.secret_key = "changememememe"


def read_credentials():
    with open("../p.txt", "r") as f:
        lines = f.readlines()
        user = lines[0].strip()
        pw = lines[1].strip()

    return user, pw


@app.route('/', methods=['GET', 'POST'])
def index():
    user, pw = read_credentials()
    message = "Failure to login"
    try:
        g = Github(user, pw)
        message = "Logged in"
    except:
        message="Failure to login"

    return render_template('index.html', message=message)

if __name__ == "__main__":
    app.run()
