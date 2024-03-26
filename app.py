from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gpa')
def gpa_tracker():
    return render_template('gpa.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/planner')
def planner():
    return render_template('planner.html')

if __name__ == "__main__":
    app.run(debug=True)